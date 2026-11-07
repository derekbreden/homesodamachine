//! Faucet stack, continuous tube paths, display placement and umbilical recipes.
use crate::assembly_dimensions::Dimensions;
use anyhow::{Context, Result, bail};
use hsm_kernel::part::Numbers;
use serde_json::{Value, json};

pub fn axis(organizer: &Value, name: &str) -> Vec<f64> {
    organizer["BORES"]
        .as_array()
        .unwrap()
        .iter()
        .find(|r| r[0] == name)
        .unwrap()[1]
        .as_array()
        .unwrap()
        .iter()
        .map(|v| v.as_f64().unwrap())
        .collect()
}
pub fn d2(a: &[f64], b: &[f64]) -> f64 {
    (a[0] - b[0]).hypot(a[1] - b[1])
}
fn number(v: &Value, k: &str) -> f64 {
    v[k].as_f64().unwrap()
}
fn p(v: &Value) -> [f64; 3] {
    [
        v[0].as_f64().unwrap(),
        v[1].as_f64().unwrap(),
        v[2].as_f64().unwrap(),
    ]
}
fn point2(v: &Value) -> [f64; 2] {
    [v[0].as_f64().unwrap(), v[1].as_f64().unwrap()]
}
fn measure(paths: Value, hulls: Value) -> Result<Value> {
    hsm_faucet::metrics::measure(&Numbers::from_value(json!({"paths":paths,"hulls":hulls})))
}
#[derive(Clone)]
pub enum Leg {
    Line([f64; 3], [f64; 3]),
    Arc([f64; 3], [f64; 3], [f64; 3]),
    Spline(Vec<[f64; 3]>),
    Hermite([f64; 3], [f64; 3], [f64; 3], [f64; 3]),
}
impl Leg {
    fn json(&self) -> Value {
        match self {
            Self::Line(a, b) => json!({"line":[a,b]}),
            Self::Arc(a, m, b) => json!({"arc":[a,m,b]}),
            Self::Spline(points) => json!({"spline":points}),
            Self::Hermite(a, b, ta, tb) => json!({"hermite":[a,b,ta,tb]}),
        }
    }
    fn legacy(&self) -> Value {
        match self {
            Self::Line(a, b) => json!(["line", a, b]),
            Self::Arc(a, m, b) => json!(["arc", a, m, b]),
            Self::Spline(points) => json!(["spline", points]),
            Self::Hermite(a, b, ta, tb) => json!(["hermite", a, b, ta, tb]),
        }
    }
    fn moved(&self, by: [f64; 3]) -> Self {
        let at = |q: [f64; 3]| [q[0] + by[0], q[1] + by[1], q[2] + by[2]];
        match self {
            Self::Line(a, b) => Self::Line(at(*a), at(*b)),
            Self::Arc(a, m, b) => Self::Arc(at(*a), at(*m), at(*b)),
            Self::Spline(v) => Self::Spline(v.iter().map(|q| at(*q)).collect()),
            Self::Hermite(a, b, ta, tb) => Self::Hermite(at(*a), at(*b), *ta, *tb),
        }
    }
    fn reversed(&self) -> Result<Self> {
        Ok(match self {
            Self::Line(a, b) => Self::Line(*b, *a),
            Self::Arc(a, m, b) => Self::Arc(*b, *m, *a),
            _ => bail!("only line and arc legs are walked backwards here"),
        })
    }
}
fn json_legs(v: &[Leg]) -> Value {
    json!(v.iter().map(Leg::json).collect::<Vec<_>>())
}
fn legacy(v: &[Leg]) -> Value {
    json!(v.iter().map(Leg::legacy).collect::<Vec<_>>())
}
fn path_legs(kind: &str, bottom: f64, sign: f64) -> Vec<Leg> {
    crate::path_legs(kind, bottom, sign, None)
        .iter()
        .map(|r| match r[0].as_str().unwrap() {
            "line" => Leg::Line(p(&r[1]), p(&r[2])),
            "arc" => Leg::Arc(p(&r[1]), p(&r[2]), p(&r[3])),
            "spline" => Leg::Spline(r[1].as_array().unwrap().iter().map(p).collect()),
            _ => unreachable!(),
        })
        .collect()
}
pub fn arc_from_tangent(
    start: [f64; 2],
    tangent: [f64; 2],
    radius: f64,
    theta: f64,
    ccw: bool,
) -> [[f64; 2]; 3] {
    let sign = if ccw { 1.0 } else { -1.0 };
    let perp = if ccw {
        [-tangent[1], tangent[0]]
    } else {
        [tangent[1], -tangent[0]]
    };
    let center = [start[0] + radius * perp[0], start[1] + radius * perp[1]];
    let rad = [start[0] - center[0], start[1] - center[1]];
    let rot = |v: [f64; 2], a: f64| {
        let (c, s) = (a.cos(), a.sin());
        [v[0] * c - v[1] * s, v[0] * s + v[1] * c]
    };
    let mid = rot(rad, sign * theta / 2.0);
    let end = rot(rad, sign * theta);
    [
        [center[0] + mid[0], center[1] + mid[1]],
        [center[0] + end[0], center[1] + end[1]],
        rot(tangent, sign * theta),
    ]
}
impl Dimensions {
    pub fn return_x(&self, s: f64) -> f64 {
        s * self.flavor_tube_x_offset
    }
    pub fn flavor_mount_x(&self, s: f64) -> f64 {
        crate::LOWER_BUNDLE_X + s * self.flavor_tube_x_offset
    }
    pub fn organizer_flavor_xy(&self, s: f64) -> Vec<f64> {
        axis(
            &crate::organizer()["datums"],
            if s > 0.0 { "F1" } else { "F2" },
        )
    }
    pub fn step_theta(&self, s: f64) -> f64 {
        let offset = d2(
            &self.organizer_flavor_xy(s),
            &[self.return_x(s), self.flavor_tube_depth_lower],
        );
        (1.0 - offset / (2.0 * self.step_bend_radius)).acos()
    }
    pub fn gather_offset(&self, s: f64) -> f64 {
        (s * self.flavor_tube_x_offset - self.return_x(s))
            .hypot(self.pack_flavor_depth - self.flavor_tube_depth_lower)
    }
    pub fn gather_theta(&self, s: f64) -> f64 {
        (1.0 - self.gather_offset(s) / (2.0 * self.umbilical_bend_radius)).acos()
    }
    pub fn gather_rise(&self, s: f64) -> f64 {
        2.0 * self.umbilical_bend_radius * self.gather_theta(s).sin()
    }
    pub fn gooseneck(
        &self,
        start: [f64; 2],
        tan: [f64; 2],
        r1: f64,
        r2: f64,
    ) -> ([[f64; 2]; 2], [f64; 2], [[f64; 2]; 2], [f64; 2]) {
        let [m1, e1, t1] = arc_from_tangent(start, tan, r1, self.gn_bend1_sweep_rad, true);
        let mid = [
            e1[0] + self.gn_mid_straight_len * t1[0],
            e1[1] + self.gn_mid_straight_len * t1[1],
        ];
        let [m2, e2, t2] = arc_from_tangent(mid, t1, r2, self.gn_bend2_sweep_rad, true);
        let tip = [
            e2[0] + self.gn_tip_straight_len * t2[0],
            e2[1] + self.gn_tip_straight_len * t2[1],
        ];
        ([m1, e1], mid, [m2, e2], tip)
    }
    pub fn soda_legs(&self) -> Vec<Leg> {
        let world = |v: [f64; 2]| {
            [
                0.0,
                self.port_center_depth + v[0],
                self.soda_faucet_tube_z_bottom + v[1],
            ]
        };
        let start = [0.0, self.gn_bend1_start_z - self.soda_faucet_tube_z_bottom];
        let (a, mid, b, tip) = self.gooseneck(start, [0.0, 1.0], self.gn_bend1_r, self.gn_bend2_r);
        let mut legs = vec![
            Leg::Line(world([0.0, 0.0]), world(start)),
            Leg::Arc(world(start), world(a[0]), world(a[1])),
        ];
        if self.gn_mid_straight_len > 0.0 {
            legs.push(Leg::Line(world(a[1]), world(mid)));
        }
        legs.extend([
            Leg::Arc(world(mid), world(b[0]), world(b[1])),
            Leg::Line(world(b[1]), world(tip)),
        ]);
        legs
    }
    pub fn step_legs(&self, s: f64, bottom: f64) -> Vec<Leg> {
        let mut legs = vec![];
        let mut current = [0.0; 3];
        let mount = [self.flavor_mount_x(s), self.flavor_tube_depth_lower];
        for (dest, z) in [
            (self.organizer_flavor_xy(s), self.mount_return_start_z),
            (
                vec![self.return_x(s), self.flavor_tube_depth_lower],
                self.organizer_return_start_z,
            ),
        ] {
            let start = [
                current[0],
                current[1],
                z - self.under_counter_plate_bottom_z,
            ];
            if crate::shell::dist(current, start) > 1e-7 {
                legs.push(Leg::Line(current, start));
            }
            let dx = dest[0] - mount[0] - start[0];
            let dy = dest[1] - mount[1] - start[1];
            let offset = dx.hypot(dy);
            if offset < 1e-7 {
                current = start;
                continue;
            }
            let theta = (1.0 - offset / (2.0 * self.step_bend_radius)).acos();
            let (ux, uy) = (dx / offset, dy / offset);
            let world = |q: [f64; 2]| [start[0] + ux * q[0], start[1] + uy * q[0], q[1]];
            let mut local = [0.0, start[2]];
            let mut tangent = [0.0, -1.0];
            for turn in [true, false] {
                let [m, e, t] = arc_from_tangent(
                    local,
                    if turn { [0.0, -1.0] } else { tangent },
                    self.step_bend_radius,
                    theta,
                    turn,
                );
                legs.push(Leg::Arc(world(local), world(m), world(e)));
                local = e;
                tangent = t;
            }
            current = [dest[0] - mount[0], dest[1] - mount[1], local[1]];
        }
        let end = [
            current[0],
            current[1],
            bottom - self.under_counter_plate_bottom_z,
        ];
        if crate::shell::dist(current, end) > 1e-7 {
            legs.push(Leg::Line(current, end));
        }
        legs
    }
    pub fn gather_legs(&self, s: f64, top: f64) -> Vec<Leg> {
        let dx = s * self.flavor_tube_x_offset - self.return_x(s);
        let dy = self.pack_flavor_depth - self.flavor_tube_depth_lower;
        let (ux, uy) = (dx / self.gather_offset(s), dy / self.gather_offset(s));
        let world = |p: [f64; 2]| [ux * p[0], uy * p[0], p[1]];
        let [m1, e1, t1] = arc_from_tangent(
            [0.0, 0.0],
            [0.0, -1.0],
            self.umbilical_bend_radius,
            self.gather_theta(s),
            true,
        );
        let [m2, e2, _] = arc_from_tangent(
            e1,
            t1,
            self.umbilical_bend_radius,
            self.gather_theta(s),
            false,
        );
        let mut at = [0.0, top - self.gather_start_z];
        let mut legs = vec![];
        if top - self.gather_start_z > 1e-9 {
            legs.push(Leg::Line(world(at), world([0.0, 0.0])));
            at = [0.0, 0.0];
        }
        legs.extend([
            Leg::Arc(world(at), world(m1), world(e1)),
            Leg::Arc(world(e1), world(m2), world(e2)),
            Leg::Line(
                world(e2),
                world([e2[0], self.splay_top_z - self.gather_start_z]),
            ),
        ]);
        legs
    }
    pub fn splay_legs(&self, s: f64) -> Vec<Leg> {
        let world = |p: [f64; 2]| [p[0], 0.0, p[1]];
        let start = [0.0, 0.0];
        let [m1, e1, t1] = arc_from_tangent(
            start,
            [0.0, -1.0],
            self.splay_bend_radius,
            self.splay_theta_rad,
            s > 0.0,
        );
        let [m2, e2, _] = arc_from_tangent(
            e1,
            t1,
            self.splay_bend_radius,
            self.splay_theta_rad,
            s < 0.0,
        );
        vec![
            Leg::Arc(world(start), world(m1), world(e1)),
            Leg::Arc(world(e1), world(m2), world(e2)),
            Leg::Line(
                world(e2),
                world([e2[0], self.umbilical_tail_z - self.splay_top_z]),
            ),
        ]
    }
    pub fn bundle_circles(&self, g: f64) -> Vec<[f64; 3]> {
        vec![
            [0.0, 0.0, self.foam_r + g],
            [
                self.flavor_tube_x_offset,
                self.pack_flavor_depth,
                self.flavor_tube_r + g,
            ],
            [
                -self.flavor_tube_x_offset,
                self.pack_flavor_depth,
                self.flavor_tube_r + g,
            ],
            [self.drain_tail_x, self.drain_pack_y, self.drain_tube_r + g],
        ]
    }
    pub fn bare_circles(&self, g: f64) -> Vec<[f64; 3]> {
        vec![
            [0.0, 0.0, self.soda_umbilical_tube_r + g],
            [
                self.return_x(1.0),
                self.flavor_tube_depth_lower,
                self.flavor_tube_r + g,
            ],
            [
                self.return_x(-1.0),
                self.flavor_tube_depth_lower,
                self.flavor_tube_r + g,
            ],
            [
                self.drain_tail_x,
                self.drain_bypass_y,
                self.drain_tube_r + g,
            ],
        ]
    }
    pub fn gather_circles(&self, g: f64) -> Vec<[f64; 3]> {
        let mut c = vec![[0.0, 0.0, self.foam_r + g]];
        for [x, y] in [
            [self.return_x(1.0), self.flavor_tube_depth_lower],
            [self.return_x(-1.0), self.flavor_tube_depth_lower],
            [self.flavor_tube_x_offset, self.pack_flavor_depth],
            [-self.flavor_tube_x_offset, self.pack_flavor_depth],
        ] {
            c.push([x, y, self.flavor_tube_r + g]);
        }
        for y in [self.drain_pack_y, self.drain_bypass_y] {
            c.push([self.drain_tail_x, y, self.drain_tube_r + g]);
        }
        c.iter()
            .enumerate()
            .filter(|(i, q)| {
                !c.iter()
                    .enumerate()
                    .any(|(j, o)| j != *i && (q[0] - o[0]).hypot(q[1] - o[1]) + q[2] <= o[2] + 1e-9)
            })
            .map(|(_, v)| *v)
            .collect()
    }
    pub fn finish_dimensions(&mut self) -> Result<()> {
        let mut paths =
            json!({"soda":json_legs(&self.soda_legs()),"splay":json_legs(&self.splay_legs(1.0))});
        for s in [1.0, -1.0] {
            let suffix = if s > 0.0 { "pos" } else { "neg" };
            paths[format!("flavor_{suffix}")] =
                json_legs(&path_legs("flavor", self.under_counter_plate_bottom_z, s));
            paths[format!("step_{suffix}")] = json_legs(&self.step_legs(s, self.gather_start_z));
        }
        self._dimension_paths = paths.clone();
        self._factory_metrics = measure(
            paths,
            json!({"pack":self.bundle_circles(self.cable_lane),"bare":self.bare_circles(self.cable_lane)}),
        )?;
        let m = &self._factory_metrics;
        self.soda_faucet_cut_length = number(&m["lengths"], "soda").ceil();
        self.sleeve_center_y = m["hulls"]["pack"]["center"][1].as_f64().unwrap();
        self.splay_extra_length =
            number(&m["lengths"], "splay") - (self.splay_top_z - self.umbilical_tail_z);
        self.flavor_cut_length = (self.blue_cut_length
            + self
                .flavor_path_above_pack(1.0)?
                .max(self.flavor_path_above_pack(-1.0)?)
            + self.splay_extra_length
            + self.umbilical_z_bottom
            - self.soda_umbilical_tube_z_top)
            .ceil();
        self._tail_planes = vec![
            self.soda_umbilical_tube_z_top - self.blue_cut_length,
            self.tail_z(1.0)?,
            self.tail_z(-1.0)?,
        ];
        self.tails_apart = self
            ._tail_planes
            .iter()
            .copied()
            .fold(f64::NEG_INFINITY, f64::max)
            - self
                ._tail_planes
                .iter()
                .copied()
                .fold(f64::INFINITY, f64::min);
        self.countertop_hole_center_y = self.seated_hole_center_y();
        self.countertop_hole_margin = self.shank_hole_margin(self.countertop_hole_center_y);
        self.collar_tails = vec![
            ("carb".to_owned(), 0.0, 0.0),
            (
                "flavor-a".to_owned(),
                self.tail_half_x,
                self.pack_flavor_depth,
            ),
            (
                "flavor-b".to_owned(),
                -self.tail_half_x,
                self.pack_flavor_depth,
            ),
            ("drain".to_owned(), self.drain_tail_x, self.drain_tail_y),
        ];
        if self.foam_z_bottom >= self.foam_z_top {
            bail!("the drawn umbilical leaves no foam below the pack; draw it longer");
        }
        Ok(())
    }
    pub fn flavor_path_above_pack(&self, s: f64) -> Result<f64> {
        let in_pack = (self.gather_start_z - self.gather_rise(s)) - self.umbilical_z_bottom;
        let carried = if s == 1.0 || s == -1.0 {
            let suffix = if s > 0.0 { "pos" } else { "neg" };
            number(
                &self._factory_metrics["lengths"],
                &format!("flavor_{suffix}"),
            ) + number(&self._factory_metrics["lengths"], &format!("step_{suffix}"))
        } else {
            let m = measure(
                json!({"flavor":json_legs(&path_legs("flavor",self.under_counter_plate_bottom_z,s)),"step":json_legs(&self.step_legs(s,self.gather_start_z))}),
                json!({}),
            )?;
            number(&m["lengths"], "flavor") + number(&m["lengths"], "step")
        };
        Ok(carried + 2.0 * self.umbilical_bend_radius * self.gather_theta(s) + in_pack)
    }
    pub fn tail_z(&self, s: f64) -> Result<f64> {
        Ok(self.umbilical_z_bottom
            - (self.flavor_cut_length - self.flavor_path_above_pack(s)? - self.splay_extra_length))
    }
    pub fn flavor_run(&self, s: f64) -> Result<Vec<Leg>> {
        let at = [
            self.flavor_mount_x(s),
            self.flavor_tube_depth_lower,
            self.under_counter_plate_bottom_z,
        ];
        let step = self.step_legs(s, self.gather_start_z);
        let mut legs = step
            .iter()
            .rev()
            .map(|l| l.moved(at).reversed())
            .collect::<Result<Vec<_>>>()?;
        legs.extend(path_legs("flavor", self.under_counter_plate_bottom_z, s));
        Ok(legs)
    }
    pub fn flavor_umbilical(&self, s: f64) -> Vec<Leg> {
        let a = [
            self.return_x(s),
            self.flavor_tube_depth_lower,
            self.gather_start_z,
        ];
        let b = [
            s * self.flavor_tube_x_offset,
            self.pack_flavor_depth,
            self.splay_top_z,
        ];
        self.gather_legs(s, self.gather_start_z)
            .iter()
            .map(|l| l.moved(a))
            .chain(self.splay_legs(s).iter().map(|l| l.moved(b)))
            .collect()
    }
    pub fn drain_lower(&self) -> Result<Vec<Leg>> {
        let mut legs = vec![];
        let mut current = [self.drain_tail_x, self.drain_tail_y, self.umbilical_tail_z];
        let org = axis(&crate::organizer()["datums"], "D");
        for [x, y, z] in [
            [self.drain_tail_x, self.drain_pack_y, self.drain_splay_top_z],
            [self.drain_tail_x, self.drain_bypass_y, self.gather_start_z],
            [org[0], org[1], self.organizer_return_start_z],
            [
                crate::LOWER_BUNDLE_X,
                crate::LOWER_DRAIN_Y,
                self.mount_return_start_z,
            ],
        ] {
            let (dx, dy) = (x - current[0], y - current[1]);
            let offset = dx.hypot(dy);
            let theta = (1.0 - offset / (2.0 * self.drain_bend_radius)).acos();
            let rise = 2.0 * self.drain_bend_radius * theta.sin();
            let start = [current[0], current[1], z - rise];
            if start[2] < current[2] - 1e-7 {
                bail!("drain return arcs exceed the available vertical run");
            }
            if crate::shell::dist(current, start) > 1e-7 {
                legs.push(Leg::Line(current, start));
            }
            let (ux, uy) = (dx / offset, dy / offset);
            let world = |q: [f64; 2]| [start[0] + ux * q[0], start[1] + uy * q[0], q[1]];
            let mut local = [0.0, start[2]];
            let mut tangent = [0.0, 1.0];
            for turn in [false, true] {
                let [m, e, t] = arc_from_tangent(
                    local,
                    if !turn { [0.0, 1.0] } else { tangent },
                    self.drain_bend_radius,
                    theta,
                    turn,
                );
                legs.push(Leg::Arc(world(local), world(m), world(e)));
                local = e;
                tangent = t;
            }
            current = [x, y, z];
        }
        if self.mount_return_lead > 1e-7 {
            legs.push(Leg::Line(
                current,
                [
                    crate::LOWER_BUNDLE_X,
                    crate::LOWER_DRAIN_Y,
                    self.under_counter_plate_bottom_z,
                ],
            ));
        }
        Ok(legs)
    }
    pub fn drain_legs(&self) -> Result<Vec<Leg>> {
        let mut legs = self.drain_lower()?;
        legs.extend(path_legs("drain", self.under_counter_plate_bottom_z, 1.0));
        Ok(legs)
    }
    pub fn drain_cut_length(&self) -> Result<f64> {
        let m = measure(json!({"drain":json_legs(&self.drain_legs()?)}), json!({}))?;
        Ok((number(&m["lengths"], "drain") + self.blue_cut_length - self.umbilical_drawn).ceil())
    }
    pub fn shank_hole_margin(&self, c: f64) -> f64 {
        self.hole_radius - (c.abs() + self.shank_od / 2.0)
    }
    pub fn flavor_hole_margin(&self, c: f64) -> f64 {
        [1.0, -1.0]
            .iter()
            .map(|s| {
                self.hole_radius
                    - self
                        .flavor_mount_x(*s)
                        .hypot(self.flavor_tube_depth_lower - c)
                    - self.flavor_tube_r
            })
            .fold(f64::INFINITY, f64::min)
    }
    pub fn seated_hole_center_y(&self) -> f64 {
        let mut rows = vec![
            [
                self.flavor_mount_x(1.0),
                self.flavor_tube_depth_lower,
                self.flavor_tube_r,
            ],
            [
                self.flavor_mount_x(-1.0),
                self.flavor_tube_depth_lower,
                self.flavor_tube_r,
            ],
            [
                crate::LOWER_BUNDLE_X,
                crate::LOWER_DRAIN_Y,
                self.drain_tube_r,
            ],
        ];
        let mut limits: Vec<_> = rows
            .drain(..)
            .map(|[x, y, r]| y - ((self.hole_radius - r).powi(2) - x * x).sqrt())
            .collect();
        for dx in [-self.cable_width / 2.0, self.cable_width / 2.0] {
            for dy in [-self.cable_lane / 2.0, self.cable_lane / 2.0] {
                limits.push(
                    self.shell.signal_lower_exit_y + dy
                        - (self.hole_radius.powi(2)
                            - (self.shell.signal_lower_exit_x + dx).powi(2))
                        .sqrt(),
                );
            }
        }
        limits.into_iter().fold(f64::NEG_INFINITY, f64::max)
    }
    pub fn gasket_hole_cover(&self) -> f64 {
        let rx = self.shell.foot_width / 2.0;
        let ry = self.shell.foot_depth / 2.0;
        let dy = self.countertop_hole_center_y - self.shell.foot_center_y;
        let mut c = vec![(ry - dy).abs(), (-ry - dy).abs()];
        if ry != rx {
            let sine = ry * dy / (ry * ry - rx * rx);
            if (-1.0..=1.0).contains(&sine) {
                c.push((rx * (1.0 - sine * sine).sqrt()).hypot(ry * sine - dy));
            }
        }
        c.into_iter().fold(f64::INFINITY, f64::min) - self.hole_radius
    }
    pub fn collar_azimuth(&self, x: f64, y: f64) -> f64 {
        let (ux, uy) = (x - 0.0, y - self.sleeve_center_y);
        let reach = ux.hypot(uy);
        (-ux / reach).atan2(uy / reach) * (180.0 / std::f64::consts::PI)
    }
    pub fn display_seat(&self) -> (f64, [f64; 3]) {
        let angle = self.gn_bend1_sweep_rad + self.gn_bend2_sweep_rad - std::f64::consts::PI / 2.0;
        let [end, up, normal] = self.shell.tip_frame();
        let along = self.display_housing_length / 2.0
            + self.shell.display_s_bottom
            + self.shell.display_cradle_clearance;
        let mut seat = [0.0; 3];
        for i in 0..3 {
            seat[i] = end[i] + normal[i] * self.shell.display_floor_n;
            seat[i] += up[i] * along;
        }
        (angle * (180.0 / std::f64::consts::PI), seat)
    }
    pub fn lever_offset(&self) -> Result<[f64; 3]> {
        let frame: Value = serde_json::from_slice(&std::fs::read(
            self.root
                .join("hardware/printed-parts/faucet/lever-replica/lever-replica.frame.json"),
        )?)?;
        Ok([
            0.0,
            self.lever_aft_y - frame["bounds_mm"][1][1].as_f64().unwrap(),
            self.lever_top_z - frame["bounds_mm"][1][2].as_f64().unwrap(),
        ])
    }
    pub fn ribbon_return(&self) -> Vec<Leg> {
        let xy = [
            self.shell.signal_lower_exit_x,
            self.shell.signal_lower_exit_y,
        ];
        let og = crate::organizer();
        let cable = &og["datums"]["CABLE_XY"];
        let (cx, cy) = (cable[0].as_f64().unwrap(), cable[1].as_f64().unwrap());
        let eased = [cx, cy, self.organizer_top_z + 12.0];
        let down = [0.0, 0.0, -1.0];
        let mut legs = vec![];
        if self.mount_return_lead > 1e-7 {
            legs.push(Leg::Line(
                [xy[0], xy[1], self.under_counter_plate_bottom_z],
                [xy[0], xy[1], self.mount_return_start_z],
            ));
        }
        legs.extend([
            Leg::Hermite([xy[0], xy[1], self.mount_return_start_z], eased, down, down),
            Leg::Line(eased, [cx, cy, self.organizer_bottom_z - 10.0]),
        ]);
        legs
    }
}
impl Dimensions {
    pub fn component_envelopes(&self) -> Result<Vec<Value>> {
        let buttons = self._display_buttons["buttons"]
            .as_array()
            .context("display buttons")?;
        let mut out = vec![];
        for row in self._display_components["components"]
            .as_array()
            .context("display components")?
        {
            if buttons
                .iter()
                .any(|b| b["vendor_solid_index"] == row["vendor_solid_index"])
            {
                continue;
            }
            if let Some(c) = row.get("conservative_cylinder") {
                let at = [
                    c["center_xy_mm"][0].as_f64().unwrap(),
                    c["center_xy_mm"][1].as_f64().unwrap(),
                    c["z_mm"][0].as_f64().unwrap(),
                ];
                out.push(json!([
                    "cylinder",
                    at,
                    c["radius_mm"],
                    c["z_mm"][1].as_f64().unwrap() - at[2]
                ]));
            } else {
                let lo = p(&row["bounds_mm"][0]);
                let hi = p(&row["bounds_mm"][1]);
                let top = hi[2].max(self.display_pcb_bottom_z + 0.02);
                out.push(json!(["box", lo, [hi[0], hi[1], top]]));
            }
        }
        Ok(out)
    }
    pub fn ribbon_spans(&self) -> Vec<Value> {
        let s = &self.shell;
        let section = |origin: [f64; 3], normal: [f64; 3], width: f64| json!({"origin":origin,"xdir":[1.0,0.0,0.0],"normal":normal,"rect":[width,s.signal_ribbon_max_depth]});
        let lower = |z: f64| {
            let a = crate::lower_point(z - 0.001, "ribbon", 1.0);
            let b = crate::lower_point(z + 0.001, "ribbon", 1.0);
            let tangent = [
                (b[0] - a[0]) / 0.002,
                (b[1] - a[1]) / 0.002,
                (b[2] - a[2]) / 0.002,
            ];
            section(
                crate::lower_point(z, "ribbon", 1.0),
                tangent,
                s.signal_ribbon_max_width,
            )
        };
        let arc = |t: f64| {
            let a = crate::tube_arc_point(t - 0.001, "ribbon", 1.0);
            let b = crate::tube_arc_point(t + 0.001, "ribbon", 1.0);
            let tangent = [
                (b[0] - a[0]) / 0.002,
                (b[1] - a[1]) / 0.002,
                (b[2] - a[2]) / 0.002,
            ];
            section(
                crate::tube_arc_point(t, "ribbon", 1.0),
                tangent,
                crate::positions(t)[4],
            )
        };
        let transition = |start: f64, end: f64, frame: &dyn Fn(f64) -> Value| {
            let count = (((end - start) / 0.3).ceil() as usize).max(2);
            json!({"loft":(0..=count).map(|i|frame(start+(end-start)*i as f64/count as f64)).collect::<Vec<_>>()})
        };
        let straight = |z0: f64, z1: f64| json!({"extrude":{"section":section(crate::lower_point(z0,"ribbon",1.0),[0.0,0.0,1.0],s.signal_ribbon_max_width),"by":[0.0,0.0,z1-z0]}});
        let constant = |s0: f64, s1: f64, n: f64| {
            let a = crate::JOINT_ANGLE + s0 / crate::water_radius();
            let b = crate::JOINT_ANGLE + s1 / crate::water_radius();
            let start = crate::arc_point(a, 0.0, n);
            json!({"sweep":{"section":section(start,[0.0,-a.sin(),a.cos()],s.signal_ribbon_max_width),"arc":[start,crate::arc_point((a+b)/2.0,0.0,n),crate::arc_point(b,0.0,n)]}})
        };
        vec![
            straight(38.8, crate::LOWER_START_Z),
            transition(crate::LOWER_START_Z, crate::LOWER_END_Z, &lower),
            straight(crate::LOWER_END_Z, crate::arc_start_z()),
            constant(
                -crate::JOINT_ANGLE * crate::water_radius(),
                crate::converge_start_s(),
                crate::TIGHT_RIBBON_N,
            ),
            transition(
                crate::converge_start_s(),
                crate::converge_start_s() + crate::RIBBON_CONVERGE_LENGTH,
                &arc,
            ),
            constant(
                crate::converge_start_s() + crate::RIBBON_CONVERGE_LENGTH,
                s.ribbon_end_station(),
                crate::FACE_RIBBON_N,
            ),
        ]
    }
    pub fn numbers(&self, r: &Value, industrial: bool) -> Result<Value> {
        let shell = &self.shell;
        let organizer = crate::organizer();
        let og = &organizer["datums"];
        let centre = point2(&og["CENTRE_XY"]);
        let prefix = "hardware/printed-parts/faucet/";
        let path = |part: &str| format!("{prefix}{part}");
        let placed = |step: String, at: [f64; 3]| json!({"step":step,"at":at});
        let rounded = |w: f64, l: f64, rad: f64, z0: f64, z1: f64| json!({"width":w,"length":l,"r":rad,"z":[z0,z1]});
        let (turn, seat) = self.display_seat();
        let screen_z = self.display_total_depth - self.display_screen_depth;
        let lower:Vec<_>=shell.lower_signal_profiles(shell.lower_signal_ribbon.0,shell.lower_signal_ribbon.1,shell.lower_signal_ribbon.2,shell.lower_signal_ribbon.3,0.0).iter().map(|row|{let angle=row[6].as_f64().unwrap()*(std::f64::consts::PI/180.0);let mut section=json!({"origin":[row[1],row[2],row[0]],"xdir":[angle.cos(),angle.sin(),0.0],"normal":[0.0,0.0,1.0]});section[if row[5].as_bool().unwrap(){"slot"}else{"rect"}]=json!([row[3],row[4]]);section}).collect();
        let neck = |wall: f64| json!([{"hull":self.bare_circles(self.cable_lane+wall),"z":self.gather_start_z,"bottom_face":true},{"origin":[centre[0],centre[1],self.organizer_bottom_z],"xdir":[1.0,0.0,0.0],"normal":[0.0,0.0,1.0],"circle":og["OD"].as_f64().unwrap()/2.0+wall}]);
        let envelopes: Vec<_> = self
            .component_envelopes()?
            .iter()
            .map(|row| {
                if row[0] == "cylinder" {
                    json!({"cylinder":[row[1][0],row[1][1],row[1][2],row[2],row[3]]})
                } else {
                    json!({"box":[row[1],row[2]]})
                }
            })
            .collect();
        let buttons: Vec<_> = self._display_buttons["buttons"]
            .as_array()
            .unwrap()
            .iter()
            .map(|row| {
                format!(
                    "hardware/reference/touch-flo-faucet/display-reference/{}",
                    row["file"].as_str().unwrap()
                )
            })
            .collect();
        let flavors:Vec<_>=[1.0,-1.0].iter().map(|sign|Ok(json!({"side":if *sign>0.0{"pos_x"}else{"neg_x"},"run":json_legs(&self.flavor_run(*sign)?),"umbilical":json_legs(&self.flavor_umbilical(*sign))}))).collect::<Result<_>>()?;
        let collars:Vec<_>=self.collar_tails.iter().map(|(which,x,y)|{let colors= [&r["collar_palette"][which][0],&r["collar_palette"][which][1]].iter().map(|v|hsm_shared_data::color::rgb8_linear(v,false)).collect::<Result<Vec<_>>>()?;Ok(json!({"name":format!("collar_{}",which.replace('-',"_")),"step":path(&format!("tube-collar/tube-collar-{which}.step")),"length":r["collar"]["LENGTH"],"colors":colors,"azimuth":self.collar_azimuth(*x,*y),"at":[x,y,self.collar_top_z]}))}).collect::<Result<_>>()?;
        let mut out = json!({
         "name":"faucet-assembly","colors":r["colors"],"westbrass":"hardware/reference/touch-flo-faucet/westbrass-reference/westbrass-reference.step",
         "soda_faucet_tube":{"r":self.soda_faucet_tube_r,"legs":json_legs(&self.soda_legs())},
         "tpu_o_ring":placed(path("tpu-o-ring/tpu-o-ring.step"),[0.0,self.port_center_depth,self.soda_faucet_tube_z_bottom-2.1]),
         "flavor_tubes":flavors,"flavor_tube_r":self.flavor_tube_r,
         "soda_umbilical_tube":{"r":self.soda_umbilical_tube_r,"z":[self.soda_umbilical_tube_z_bottom,self.soda_umbilical_tube_z_top]},
         "drain_tube":{"r":self.drain_tube_r,"r_in":2.5/2.0,"legs":json_legs(&self.drain_legs()?)},
         "lever":placed(path("lever-replica/lever-replica.step"),self.lever_offset()?),
         "above_counter_plate":path("above-counter-plate/above-counter-plate.step"),"above_counter_gasket":path("above-counter-gasket/above-counter-gasket.step"),
         "shell_base":path("faucet-shell/faucet-shell-base.step"),"shell_tip":path("faucet-shell/faucet-shell-tip.step"),"display_cover":path("faucet-display-cover/faucet-display-cover-seated.step"),
         "base_screws":{"centres":shell.base_pod_centers,"seat_z":shell.base_screw_seat_z,"length":shell.base_screw_length,"head_height":shell.base_screw_head_height,"shaft_r":self.base_screw_shaft_r,"head_r":self.base_screw_head_r,"socket_d":self.base_screw_socket_af/(std::f64::consts::PI/6.0).cos(),"socket_depth":self.base_screw_socket_depth,"socket_below":self.base_screw_socket_below},
         "base_inserts":{"bottom_z":shell.base_insert_bottom_z,"r":shell.base_insert_outer_dia/2.0,"r_in":self.base_insert_inner_r,"length":shell.base_insert_length},
         "display":{"pcb":rounded(self.display_pcb_width,self.display_pcb_length,self.display_pcb_corner_r,self.display_pcb_bottom_z,self.display_pcb_top_z),"housing":rounded(self.display_housing_width,self.display_housing_length,self.display_corner_r,self.display_pcb_top_z,self.display_total_depth),"pocket":rounded(self.display_screen_width,self.display_screen_length,self.display_screen_corner_r,screen_z,screen_z+self.display_screen_depth+1.0),"screen":rounded(self.display_screen_width,self.display_screen_length,self.display_screen_corner_r,screen_z,screen_z+self.display_screen_depth),"envelopes":envelopes,"buttons":buttons,"turn":turn,"seat":seat},
         "ribbon":{"lower":lower,"plate_z":self.under_counter_plate_bottom_z,"return":{"width":self.cable_width,"depth":self.cable_lane,"legs":json_legs(&self.ribbon_return())},"spans":self.ribbon_spans(),"display":shell.display_ribbon_frames(shell.signal_ribbon_max_width,shell.signal_ribbon_max_depth,shell.display_ribbon_top_n)?},
         "countertop":{"size":self.countertop_slab_xy,"z":[self.countertop_bottom_z,self.countertop_top_z],"hole":[0.0,self.countertop_hole_center_y,self.hole_radius]},
         "under_counter_plate":{"dxf":"hardware/cut-parts/faucet/under-counter-plate/under-counter-plate.dxf","thickness":self.under_counter_plate_thickness,"z":self.countertop_bottom_z-self.under_counter_plate_thickness},
         "foam":{"r":self.foam_r,"r_in":self.soda_umbilical_tube_r,"z":[self.foam_z_bottom,self.foam_z_top]},
         "sleeve":{"wall":self.sleeve_wall,"gather":{"outer":self.gather_circles(self.cable_lane+self.sleeve_wall),"inner":self.gather_circles(self.cable_lane),"z":[self.umbilical_z_bottom,self.gather_start_z]},"pack":{"outer":self.bundle_circles(self.cable_lane+self.sleeve_wall),"inner":self.bundle_circles(self.cable_lane),"z":[self.sleeve_z_bottom,self.umbilical_z_bottom]},"neck":{"outer":neck(self.sleeve_wall),"inner":neck(0.0)},"ring":{"centre":centre,"r":og["OD"].as_f64().unwrap()/2.0,"z":[self.organizer_bottom_z,self.organizer_top_z]}},
         "organizer":placed(path("umbilical-organizer/umbilical-organizer.step"),[centre[0],centre[1],self.organizer_top_z-og["LENGTH"].as_f64().unwrap()]),"collars":collars
        });
        if industrial {
            out["name"] = json!("faucet-industrial-assembly");
            for (body, part) in [
                ("shell_base", "industrial-shell-base"),
                ("above_counter_plate", "industrial-above-counter-plate"),
                ("above_counter_gasket", "industrial-above-counter-gasket"),
            ] {
                out[body] = json!(path(&format!("industrial/{part}.step")));
            }
            out["display_cover"] = json!(path("industrial/industrial-display-cover-seated.step"));
        }
        Ok(out)
    }
}

fn py_float(n: f64) -> String {
    let s = n.to_string();
    if !s.contains(['.', 'e', 'E']) {
        s + ".0"
    } else {
        s
    }
}
impl Dimensions {
    pub fn report(&self, r: &Value) -> Result<Value> {
        let bend1_deg = self.gn_bend1_sweep_rad * (180.0 / std::f64::consts::PI);
        let bend2_deg = self.gn_bend2_sweep_rad * (180.0 / std::f64::consts::PI);
        let tip_below_horiz = (bend1_deg + bend2_deg) - 90.0;
        let mut lines = Vec::new();
        lines.push("Touch-Flo faucet assembly".to_owned());
        lines.push(
            [
                "  Reference Westbrass:   ".to_owned(),
                "westbrass-reference.step".to_owned(),
            ]
            .concat(),
        );
        lines.push(
            [
                "  Soda faucet tube:      Ø".to_owned(),
                hsm_documents::format_number(self.soda_faucet_tube_od, ".3f")?,
                " mm".to_owned(),
            ]
            .concat(),
        );
        lines.push(
            [
                "                         Z_bottom = ".to_owned(),
                hsm_documents::format_number(self.soda_faucet_tube_z_bottom, ".2f")?,
                " mm (".to_owned(),
                py_float(self.soda_faucet_tube_into_port),
                " mm into port)".to_owned(),
            ]
            .concat(),
        );
        lines.push(["                         vertical → gooseneck".to_owned()].concat());
        lines.push(
            [
                "                         center at X=0, Y=".to_owned(),
                hsm_documents::format_number((self.port_center_depth), ".3f")?,
                " mm".to_owned(),
            ]
            .concat(),
        );
        lines.push(
            [
                "  Flavor tubes (×2):     Ø".to_owned(),
                hsm_documents::format_number(self.flavor_tube_od, ".3f")?,
                " mm".to_owned(),
            ]
            .concat(),
        );
        lines.push(
            [
                "                         Z_bottom = ".to_owned(),
                hsm_documents::format_number(self.flavor_tube_z_bottom, ".1f")?,
                " mm".to_owned(),
            ]
            .concat(),
        );
        lines.push(
            [
                "                         lower depth = ".to_owned(),
                hsm_documents::format_number(self.flavor_tube_depth_lower, ".4f")?,
                " mm (tangent to the Westbrass's back face)".to_owned(),
            ]
            .concat(),
        );
        lines.push(
            [
                "                         tight pack depth = ".to_owned(),
                hsm_documents::format_number(self.flavor_tube_depth_upper, ".4f")?,
                " mm".to_owned(),
            ]
            .concat(),
        );
        lines.push(
            [
                "                         mounting X = ".to_owned(),
                hsm_documents::format_number(self.flavor_mount_x(-(1.0)), ".4f")?,
                ", ".to_owned(),
                hsm_documents::format_number(self.flavor_mount_x((1.0)), ".4f")?,
                " mm; pack X = ±".to_owned(),
                hsm_documents::format_number(self.flavor_tube_x_offset, ".4f")?,
                " mm".to_owned(),
            ]
            .concat(),
        );
        lines.push(
            [
                "                         smooth lower transition starts at Z = ".to_owned(),
                hsm_documents::format_number(self.pre_bend_z, ".1f")?,
            ]
            .concat(),
        );
        lines.push(
            [
                "  Gooseneck:             bend 1 ".to_owned(),
                hsm_documents::format_number(bend1_deg, ".0f")?,
                "°, bend 2 ".to_owned(),
                hsm_documents::format_number(bend2_deg, ".0f")?,
                "°, midpoint Z=".to_owned(),
                hsm_documents::format_number(self.gn_bend1_mid_z, ".1f")?,
                ", start Z=".to_owned(),
                hsm_documents::format_number(self.gn_bend1_start_z, ".2f")?,
            ]
            .concat(),
        );
        lines.push(
            [
                "                         bend 1: water R=".to_owned(),
                hsm_documents::format_number(self.gn_bend1_r, ".2f")?,
                " mm, flavor R=".to_owned(),
                hsm_documents::format_number(self.gn_flavor_bend1_r, ".2f")?,
                " mm (parallel offset)".to_owned(),
            ]
            .concat(),
        );
        lines.push(
            [
                "                         bend 2: water R=".to_owned(),
                hsm_documents::format_number(self.gn_bend2_r, ".2f")?,
                " mm, flavor R=".to_owned(),
                hsm_documents::format_number(self.gn_flavor_bend2_r, ".2f")?,
                " mm (parallel offset)".to_owned(),
            ]
            .concat(),
        );
        lines.push(
            [
                "                         ".to_owned(),
                py_float(self.gn_mid_straight_len),
                " mm angled straight @ ".to_owned(),
                hsm_documents::format_number(bend1_deg, ".0f")?,
                "° from vertical".to_owned(),
            ]
            .concat(),
        );
        lines.push(
            [
                "                         ".to_owned(),
                py_float(self.gn_tip_straight_len),
                " mm tip (".to_owned(),
                hsm_documents::format_number(tip_below_horiz, ".0f")?,
                "° below horizontal)".to_owned(),
            ]
            .concat(),
        );
        lines.push(
            [
                "  Soda umbilical tube:   Ø".to_owned(),
                hsm_documents::format_number(self.soda_umbilical_tube_od, ".3f")?,
                " mm, Z = ".to_owned(),
                hsm_documents::format_number(self.soda_umbilical_tube_z_bottom, ".1f")?,
                " → ".to_owned(),
                hsm_documents::format_number(self.soda_umbilical_tube_z_top, ".1f")?,
                " (on the shank's bottom face)".to_owned(),
            ]
            .concat(),
        );
        lines.push(
            [
                "  Flavor tubing:         continuous black 4 mm, R".to_owned(),
                hsm_documents::format_number(self.step_bend_radius, "g")?,
                " mounting returns".to_owned(),
            ]
            .concat(),
        );
        lines.push(
            [
                "  Umbilical:             gathers of ".to_owned(),
                hsm_documents::format_number(self.gather_rise((1.0)), ".2f")?,
                " (flavor-a) and ".to_owned(),
                hsm_documents::format_number(self.gather_rise(-(1.0)), ".2f")?,
                " (flavor-b) to the pack at Z = ".to_owned(),
                hsm_documents::format_number(self.umbilical_z_bottom, ".2f")?,
                ", depth ".to_owned(),
                hsm_documents::format_number(self.pack_flavor_depth, ".4f")?,
                " at X = ±".to_owned(),
                hsm_documents::format_number(self.flavor_tube_x_offset, ".4f")?,
            ]
            .concat(),
        );
        lines.push(
            [
                "                         drawn ".to_owned(),
                hsm_documents::format_number(self.umbilical_drawn, "g")?,
                " mm below the compression port, all four tails on Z = ".to_owned(),
                hsm_documents::format_number(self.umbilical_tail_z, ".1f")?,
            ]
            .concat(),
        );
        lines.push(
            [
                "  Factory cut:           blue ".to_owned(),
                hsm_documents::format_number(self.blue_cut_length, "g")?,
                ", flavour ".to_owned(),
                hsm_documents::format_number(self.flavor_cut_length, "g")?,
                " (".to_owned(),
                hsm_documents::format_number(self.flavor_path_above_pack((1.0))?, ".1f")?,
                " / ".to_owned(),
                hsm_documents::format_number(self.flavor_path_above_pack(-(1.0))?, ".1f")?,
                " of it above the pack)".to_owned(),
            ]
            .concat(),
        );
        lines.push(
            [
                "                         the three tails land within ".to_owned(),
                hsm_documents::format_number(self.tails_apart, ".2f")?,
                " mm — §1 sums them to one plane".to_owned(),
            ]
            .concat(),
        );
        lines.push(
            [
                "                         soda faucet tube ".to_owned(),
                hsm_documents::format_number(self.soda_faucet_cut_length, "g")?,
                ", in the faucet's finish".to_owned(),
            ]
            .concat(),
        );
        lines.push(
            [
                "                         4 mm DRAIN tube ".to_owned(),
                hsm_documents::format_number(self.drain_cut_length()?, "g")?,
                ", untrimmed".to_owned(),
            ]
            .concat(),
        );
        lines.push(
            [
                "  Foam (blue only):      Ø".to_owned(),
                hsm_documents::format_number(self.foam_od, "g")?,
                ", ".to_owned(),
                hsm_documents::format_number(self.foam_length, ".1f")?,
                " mm over five segments, drawn Z = ".to_owned(),
                hsm_documents::format_number(self.foam_z_bottom, ".1f")?,
                " → ".to_owned(),
                hsm_documents::format_number(self.foam_z_top, ".1f")?,
                " (".to_owned(),
                hsm_documents::format_number(self.foam_bare_at_westbrass, ".1f")?,
                " bare at the Westbrass, ".to_owned(),
                hsm_documents::format_number(self.foam_bare_at_wall, "g")?,
                " bare at the wall)".to_owned(),
            ]
            .concat(),
        );
        lines.push(
            [
                "  Sleeve:                ".to_owned(),
                hsm_documents::format_number(
                    number(&self._factory_metrics["hulls"]["pack"], "perimeter"),
                    ".2f",
                )?,
                " mm of girth, Ø".to_owned(),
                hsm_documents::format_number(
                    (number(&self._factory_metrics["hulls"]["pack"], "perimeter")
                        / std::f64::consts::PI),
                    ".2f",
                )?,
                " opened, at Y = ".to_owned(),
                hsm_documents::format_number(self.sleeve_center_y, ".4f")?,
                ", Z = ".to_owned(),
                hsm_documents::format_number(self.sleeve_z_bottom, ".1f")?,
                " → ".to_owned(),
                hsm_documents::format_number(self.umbilical_z_bottom, ".1f")?,
                " over the pack (".to_owned(),
                hsm_documents::format_number(self.foam_bare_at_wall, ".1f")?,
                " mm of bundle left bare, five segments over the foam's)".to_owned(),
            ]
            .concat(),
        );
        lines.push(
            [
                "                         ".to_owned(),
                hsm_documents::format_number(
                    number(&self._factory_metrics["hulls"]["bare"], "perimeter"),
                    ".2f",
                )?,
                " mm of girth over the bare tubes, Z = ".to_owned(),
                hsm_documents::format_number(self.umbilical_z_bottom, ".1f")?,
                " → ".to_owned(),
                hsm_documents::format_number(self.sleeve_z_top, ".2f")?,
            ]
            .concat(),
        );
        lines.push(
            [
                "  Tube collars:          ".to_owned(),
                hsm_documents::format_number(r["collar"]["OD"].as_f64().unwrap(), "g")?,
                " × ".to_owned(),
                hsm_documents::format_number(r["collar"]["LENGTH"].as_f64().unwrap(), "g")?,
                ", Z = ".to_owned(),
                hsm_documents::format_number(
                    (self.collar_top_z - r["collar"]["LENGTH"].as_f64().unwrap()),
                    ".1f",
                )?,
                " → ".to_owned(),
                hsm_documents::format_number(self.collar_top_z, ".1f")?,
                " — SODA on the blue, FLAVOR on each black".to_owned(),
            ]
            .concat(),
        );
        lines.push(
            [
                "  TPU o-ring:            in the Ø".to_owned(),
                hsm_documents::format_number(
                    crate::o_ring()["datums"]["westbrass_port_diameter"]
                        .as_f64()
                        .unwrap(),
                    ".1f",
                )?,
                " mm top port, Z = ".to_owned(),
                hsm_documents::format_number(
                    (self.soda_faucet_tube_z_bottom
                        - crate::o_ring()["datums"]["cap_thickness"]
                            .as_f64()
                            .unwrap()),
                    ".2f",
                )?,
                " → ".to_owned(),
                hsm_documents::format_number(
                    ((self.soda_faucet_tube_z_bottom
                        - crate::o_ring()["datums"]["cap_thickness"]
                            .as_f64()
                            .unwrap())
                        + crate::o_ring()["datums"]["total_height"]
                            .as_f64()
                            .unwrap()),
                    ".2f",
                )?,
            ]
            .concat(),
        );
        lines.push(["  Above-counter plate:   above-counter-plate.step".to_owned()].concat());
        lines.push(["  Above-counter gasket:  above-counter-gasket.step".to_owned()].concat());
        lines.push(["  Shell pieces:          faucet-shell.step".to_owned()].concat());
        lines.push(
            [
                "  Display cover:         ".to_owned(),
                "faucet-display-cover-seated.step".to_owned(),
            ]
            .concat(),
        );
        lines.push(
            [
                "  Countertop:            ".to_owned(),
                hsm_documents::format_number(self.countertop_thickness, ".0f")?,
                " mm slab, Z = ".to_owned(),
                hsm_documents::format_number(self.countertop_bottom_z, ".1f")?,
                " → ".to_owned(),
                hsm_documents::format_number(self.countertop_top_z, ".1f")?,
            ]
            .concat(),
        );
        lines.push(
            [
                "    standard hole:       Ø".to_owned(),
                hsm_documents::format_number(self.countertop_hole_diameter, ".2f")?,
                " mm at Y = ".to_owned(),
                hsm_documents::format_number(self.countertop_hole_center_y, ".3f")?,
                " mm — the faucet back against its wall".to_owned(),
            ]
            .concat(),
        );
        lines.push(
            [
                "                         flavor pair on the wall, ".to_owned(),
                hsm_documents::format_number(self.countertop_hole_margin, ".3f")?,
                " mm of slab forward of the shank".to_owned(),
            ]
            .concat(),
        );
        lines.push(
            [
                "                         gasket covers the hole behind by ".to_owned(),
                hsm_documents::format_number(self.gasket_hole_cover(), ".3f")?,
                " mm".to_owned(),
            ]
            .concat(),
        );
        lines.push(
            [
                "  Under-counter plate:   ".to_owned(),
                py_float(self.under_counter_plate_thickness),
                " mm 316 SS off ".to_owned(),
                "under-counter-plate.dxf".to_owned(),
                ", Z = ".to_owned(),
                hsm_documents::format_number(
                    (self.countertop_bottom_z - self.under_counter_plate_thickness),
                    ".3f",
                )?,
                " → ".to_owned(),
                hsm_documents::format_number(self.countertop_bottom_z, ".1f")?,
            ]
            .concat(),
        );
        lines.push(["-> ".to_owned(), "faucet-assembly.step".to_owned()].concat());
        let mut variables = serde_json::Map::new();
        variables.insert(
            "SODA_FAUCET_TUBE_OD".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.soda_faucet_tube_od, ".4g")?,
                    " mm".to_owned()
                ]
                .concat()
            ),
        );
        variables.insert(
            "SODA_FAUCET_TUBE_Z_BOTTOM".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.soda_faucet_tube_z_bottom, ".4g")?,
                    " mm".to_owned()
                ]
                .concat()
            ),
        );
        variables.insert(
            "SODA_FAUCET_TUBE_Z_TOP".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.soda_faucet_tube_z_top, ".4g")?,
                    " mm".to_owned()
                ]
                .concat()
            ),
        );
        variables.insert(
            "FLAVOR_TUBE_OD".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.flavor_tube_od, ".4g")?,
                    " mm".to_owned()
                ]
                .concat()
            ),
        );
        variables.insert(
            "FLAVOR_TUBE_DEPTH_LOWER".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.flavor_tube_depth_lower, ".4g")?,
                    " mm".to_owned()
                ]
                .concat()
            ),
        );
        variables.insert(
            "FLAVOR_TUBE_DEPTH_UPPER".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.flavor_tube_depth_upper, ".4f")?,
                    " mm".to_owned()
                ]
                .concat()
            ),
        );
        variables.insert(
            "FLAVOR_BEND_THETA".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.flavor_bend_theta_rad, ".4f")?,
                    " rad".to_owned()
                ]
                .concat()
            ),
        );
        variables.insert(
            "PRE_BEND_Z".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.pre_bend_z, ".4g")?,
                    " mm".to_owned()
                ]
                .concat()
            ),
        );
        variables.insert(
            "LEVER_TOP_Z".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.lever_top_z, ".4g")?,
                    " mm".to_owned()
                ]
                .concat()
            ),
        );
        variables.insert(
            "GN_BEND_MID_Z".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.gn_bend1_mid_z, ".4g")?,
                    " mm".to_owned()
                ]
                .concat()
            ),
        );
        variables.insert(
            "GN_BEND_START_Z".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.gn_bend1_start_z, ".2f")?,
                    " mm".to_owned()
                ]
                .concat()
            ),
        );
        variables.insert(
            "GN_FLAVOR_BEND_ONE_R".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.gn_flavor_bend1_r, ".4f")?,
                    " mm".to_owned()
                ]
                .concat()
            ),
        );
        variables.insert(
            "GN_FLAVOR_BEND_TWO_R".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.gn_flavor_bend2_r, ".4f")?,
                    " mm".to_owned()
                ]
                .concat()
            ),
        );
        variables.insert(
            "UMBILICAL_Z_BOTTOM".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.umbilical_z_bottom, ".4g")?,
                    " mm".to_owned()
                ]
                .concat()
            ),
        );
        variables.insert(
            "PACK_FLAVOR_DEPTH".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.pack_flavor_depth, ".4f")?,
                    " mm".to_owned()
                ]
                .concat()
            ),
        );
        variables.insert(
            "UMBILICAL_TAIL_Z".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.umbilical_tail_z, ".5g")?,
                    " mm".to_owned()
                ]
                .concat()
            ),
        );
        variables.insert(
            "TAILS_APART".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.tails_apart, ".4g")?,
                    " mm".to_owned()
                ]
                .concat()
            ),
        );
        variables.insert(
            "FOAM_BARE_AT_WESTBRASS".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.foam_bare_at_westbrass, ".4g")?,
                    " mm".to_owned()
                ]
                .concat()
            ),
        );
        variables.insert(
            "FOAM_Z_BOTTOM".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.foam_z_bottom, ".4g")?,
                    " mm".to_owned()
                ]
                .concat()
            ),
        );
        variables.insert(
            "SLEEVE_CENTER_Y".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.sleeve_center_y, ".4f")?,
                    " mm".to_owned()
                ]
                .concat()
            ),
        );
        variables.insert(
            "SLEEVE_GIRTH".to_owned(),
            json!(
                [
                    hsm_documents::format_number(
                        number(&self._factory_metrics["hulls"]["pack"], "perimeter"),
                        ".4g"
                    )?,
                    " mm".to_owned()
                ]
                .concat()
            ),
        );
        variables.insert(
            "SLEEVE_BORE".to_owned(),
            json!(
                [
                    hsm_documents::format_number(
                        (number(&self._factory_metrics["hulls"]["pack"], "perimeter")
                            / std::f64::consts::PI),
                        ".4g"
                    )?,
                    " mm".to_owned()
                ]
                .concat()
            ),
        );
        variables.insert(
            "SODA_UMBILICAL_BELOW_COUNTER".to_owned(),
            json!(
                [
                    hsm_documents::format_number(
                        (self.countertop_top_z - self.soda_umbilical_tube_z_top),
                        ".4g"
                    )?,
                    " mm".to_owned()
                ]
                .concat()
            ),
        );
        variables.insert(
            "COUNTERTOP_TOP_Z".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.countertop_top_z, ".4g")?,
                    " mm".to_owned()
                ]
                .concat()
            ),
        );
        variables.insert(
            "COUNTERTOP_BOTTOM_Z".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.countertop_bottom_z, ".4g")?,
                    " mm".to_owned()
                ]
                .concat()
            ),
        );
        variables.insert(
            "HOLE_CENTER_Y".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.countertop_hole_center_y, ".4g")?,
                    " mm".to_owned()
                ]
                .concat()
            ),
        );
        variables.insert(
            "HOLE_MARGIN".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.countertop_hole_margin, ".4g")?,
                    " mm".to_owned()
                ]
                .concat()
            ),
        );
        Ok(json!({"lines":lines,"variables":variables}))
    }
}
fn parse_legs(value: &Value) -> Result<Vec<Leg>> {
    value
        .as_array()
        .context("centreline legs")?
        .iter()
        .map(|row| {
            let kind = row[0].as_str().context("centreline kind")?;
            Ok(match kind {
                "line" => Leg::Line(p(&row[1]), p(&row[2])),
                "arc" => Leg::Arc(p(&row[1]), p(&row[2]), p(&row[3])),
                "spline" => Leg::Spline(
                    row[1]
                        .as_array()
                        .context("spline points")?
                        .iter()
                        .map(p)
                        .collect(),
                ),
                "hermite" => Leg::Hermite(p(&row[1]), p(&row[2]), p(&row[3]), p(&row[4])),
                _ => bail!("unknown centreline kind {kind}"),
            })
        })
        .collect()
}
thread_local! {static DATA:std::cell::RefCell<std::collections::HashMap<String,std::rc::Rc<Dimensions>>>=std::cell::RefCell::new(std::collections::HashMap::new());}
pub fn dispatch(r: &Value) -> Result<Value> {
    let operation = r["fn"].as_str().unwrap_or("datums");
    if operation == "_scalar_dimensions" {
        return measure(
            if r["paths"].is_object() {
                r["paths"].clone()
            } else {
                json!({})
            },
            if r["hulls"].is_object() {
                r["hulls"].clone()
            } else {
                json!({})
            },
        );
    }
    if operation == "rgb8-srgb" {
        let rows = r["rgb"].as_array().context("RGB8 triple")?;
        return Ok(json!(
            rows.iter()
                .map(|n| n.as_f64().unwrap() / 255.0)
                .collect::<Vec<_>>()
        ));
    }
    if operation == "_moved_legs" {
        let legs = parse_legs(&r["legs"])?;
        return Ok(legacy(
            &legs
                .iter()
                .map(|l| l.moved(p(&r["by"])))
                .collect::<Vec<_>>(),
        ));
    }
    if operation == "_reversed_legs" {
        let legs = parse_legs(&r["legs"])?;
        return Ok(legacy(
            &legs
                .iter()
                .rev()
                .map(Leg::reversed)
                .collect::<Result<Vec<_>>>()?,
        ));
    }
    let root = std::path::PathBuf::from(r["root"].as_str().context("faucet assembly root")?);
    let slip = r["slip"].as_f64().unwrap_or(0.15);
    let key = format!("{}:{slip}:{}", root.display(), r["collar"]);
    let existing = DATA.with(|cache| cache.borrow().get(&key).cloned());
    let data = match existing {
        Some(data) => data,
        None => {
            let data = std::rc::Rc::new(Dimensions::new(slip, &r["collar"], &root)?);
            DATA.with(|cache| cache.borrow_mut().insert(key, data.clone()));
            data
        }
    };
    let args = r["args"].as_array().cloned().unwrap_or_default();
    let f = |i: usize, default: f64| args.get(i).and_then(Value::as_f64).unwrap_or(default);
    Ok(match operation {
        "datums" => serde_json::to_value(data.as_ref())?,
        "numbers" => data.numbers(r, r["industrial"].as_bool().unwrap_or(false))?,
        "report" => data.report(r)?,
        "return_x" => json!(data.return_x(f(0, 1.0))),
        "flavor_mount_x" => json!(data.flavor_mount_x(f(0, 1.0))),
        "step_theta" => json!(data.step_theta(f(0, 1.0))),
        "organizer_flavor_xy" => json!(data.organizer_flavor_xy(f(0, 1.0))),
        "gather_offset" => json!(data.gather_offset(f(0, 1.0))),
        "gather_theta" => json!(data.gather_theta(f(0, 1.0))),
        "gather_rise" => json!(data.gather_rise(f(0, 1.0))),
        "_arc_from_tangent" => json!(arc_from_tangent(
            point2(&args[0]),
            point2(&args[1]),
            f(2, 0.0),
            f(3, 0.0),
            args[4].as_bool().unwrap()
        )),
        "_gooseneck_segments" => {
            let (a, m, b, t) =
                data.gooseneck(point2(&args[0]), point2(&args[1]), f(2, 0.0), f(3, 0.0));
            json!([a, m, b, t])
        }
        "_soda_faucet_legs" => legacy(&data.soda_legs()),
        "_step_legs" => legacy(&data.step_legs(f(0, 1.0), f(1, 0.0))),
        "_gather_legs" => legacy(&data.gather_legs(f(0, 1.0), f(1, 0.0))),
        "_splay_legs" => legacy(&data.splay_legs(f(0, 1.0))),
        "flavor_path_above_pack" => json!(data.flavor_path_above_pack(f(0, 1.0))?),
        "flavor_path_above_foot" => json!(
            number(&data._factory_metrics["lengths"], "flavor_pos")
                + data.under_counter_plate_bottom_z
        ),
        "_ribbon_return_legs" => legacy(&data.ribbon_return()),
        "_bundle_circles" => json!(data.bundle_circles(f(0, 0.0))),
        "_gather_circles" => json!(data.gather_circles(f(0, 0.0))),
        "_bare_bundle_circles" => json!(data.bare_circles(f(0, 0.0))),
        "bundle_girth" => {
            let grow = f(0, data.cable_lane);
            if grow == data.cable_lane {
                json!(number(&data._factory_metrics["hulls"]["pack"], "perimeter"))
            } else {
                json!(number(
                    &measure(json!({}), json!({"pack":data.bundle_circles(grow)}))?["hulls"]["pack"],
                    "perimeter"
                ))
            }
        }
        "bundle_bore" => json!(
            number(&data._factory_metrics["hulls"]["pack"], "perimeter") / std::f64::consts::PI
        ),
        "bare_bundle_girth" => json!(number(&data._factory_metrics["hulls"]["bare"], "perimeter")),
        "tail_z" => json!(data.tail_z(f(0, 1.0))?),
        "_drain_lower_legs" => legacy(&data.drain_lower()?),
        "drain_legs" => legacy(&data.drain_legs()?),
        "drain_factory_cut_length" => json!(data.drain_cut_length()?),
        "_lever_frame_offset" => json!(data.lever_offset()?),
        "_display_component_envelopes" => json!(data.component_envelopes()?),
        "_display_seat" => {
            let (a, p) = data.display_seat();
            json!([a, p])
        }
        "_tip_centerline_world" => {
            let (_, _, arc, tip) = data.gooseneck(
                [0.0, data.gn_bend1_start_z - data.soda_faucet_tube_z_bottom],
                [0.0, 1.0],
                data.gn_bend1_r,
                data.gn_bend2_r,
            );
            json!([
                [
                    0.0,
                    arc[1][0] + data.port_center_depth,
                    arc[1][1] + data.soda_faucet_tube_z_bottom
                ],
                [
                    0.0,
                    tip[0] + data.port_center_depth,
                    tip[1] + data.soda_faucet_tube_z_bottom
                ]
            ])
        }
        "shank_hole_margin" => json!(data.shank_hole_margin(f(0, 0.0))),
        "flavor_hole_margin" => json!(data.flavor_hole_margin(f(0, 0.0))),
        "seated_hole_center_y" => json!(data.seated_hole_center_y()),
        "gasket_hole_cover" => json!(data.gasket_hole_cover()),
        "_collar_azimuth" => json!(data.collar_azimuth(f(0, 0.0), f(1, 0.0))),
        "flavor_run_legs" => legacy(&data.flavor_run(f(0, 1.0))?),
        "flavor_umbilical_legs" => legacy(&data.flavor_umbilical(f(0, 1.0))),
        "ribbon_spans" => json!(data.ribbon_spans()),
        name => bail!("unknown faucet assembly scalar operation {name}"),
    })
}
