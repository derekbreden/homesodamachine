//! Scalar sections, passage sampling and manufacturing data for the faucet shell.
#![allow(unused_parens)]
use crate::shell_dimensions::Dimensions;
use anyhow::{Context, Result, bail};
use serde_json::{Value, json};

impl Dimensions {
    pub fn bend2_point(&self, rot: f64) -> [f64; 2] {
        [
            self._path_center_bend2[0] - self.gn_bend2_r * rot.cos(),
            self._path_center_bend2[1] + self.gn_bend2_r * rot.sin(),
        ]
    }
    pub fn lower_signal_stations(&self) -> Vec<[f64; 4]> {
        vec![
            [
                14.0,
                self.signal_lower_exit_x,
                self.signal_lower_exit_y,
                0.0,
            ],
            [
                39.0,
                self.signal_lower_exit_x,
                self.signal_lower_exit_y,
                0.0,
            ],
        ]
    }
    pub fn lower_signal_profiles(
        &self,
        width: f64,
        depth: f64,
        rounded: bool,
        bottom_z: f64,
        clearance: f64,
    ) -> Vec<Value> {
        let stations = self.lower_signal_stations();
        let mut profiles = vec![];
        for z in [bottom_z, stations[0][0] - 1.0] {
            profiles.push(json!([
                z,
                self.signal_lower_exit_x,
                self.signal_lower_exit_y,
                width,
                depth,
                rounded,
                self.signal_lower_exit_angle
            ]));
        }
        let mut turns = vec![stations[0]];
        for w in stations.windows(2) {
            let a = w[0];
            let b = w[1];
            let count = if a[3] != b[3] {
                (((b[0] - a[0]) / 0.25).ceil() as usize).max(1)
            } else {
                1
            };
            for i in 1..=count {
                let mut row = [0.0; 4];
                for j in 0..4 {
                    row[j] = a[j] + (b[j] - a[j]) * i as f64 / count as f64;
                }
                turns.push(row);
            }
        }
        for [z, x, y, angle] in turns {
            profiles.push(json!([
                z,
                x,
                y,
                width + 2.0 * clearance,
                depth + 2.0 * clearance,
                rounded,
                angle
            ]));
        }
        profiles
    }
    pub fn lower_heights(&self) -> Vec<f64> {
        let z0 = crate::LOWER_START_Z;
        let z1 = crate::LOWER_END_Z;
        let n = ((z1 - z0) / 0.4).ceil() as usize;
        (0..=n)
            .map(|i| z0 + (z1 - z0) * i as f64 / n as f64)
            .collect()
    }
    pub fn lower_circles(&self, z: f64) -> Vec<[f64; 3]> {
        let left = crate::lower_point(z, "flavor", -1.0);
        let right = crate::lower_point(z, "flavor", 1.0);
        let ribbon = crate::lower_point(z, "ribbon", 1.0);
        let drain = crate::lower_point(z, "drain", 1.0);
        let half = (self.signal_lane_width - self.signal_lane_depth) / 2.0;
        vec![
            [
                0.0,
                self.soda_faucet_tube_y,
                self.soda_faucet_hole_diameter / 2.0,
            ],
            [left[0], left[1], self.flavor_tube_hole_dia / 2.0],
            [right[0], right[1], self.flavor_tube_hole_dia / 2.0],
            [drain[0], drain[1], (4.0 + 0.9) / 2.0],
            [ribbon[0] - half, ribbon[1], self.signal_lane_depth / 2.0],
            [ribbon[0] + half, ribbon[1], self.signal_lane_depth / 2.0],
        ]
    }
    pub fn tube_circles(&self, include_signal: bool, station: f64) -> Vec<[f64; 3]> {
        let [x, n, _, ribbon, _] = crate::positions(station);
        let mut rows = vec![
            [0.0, 0.0, self.soda_faucet_hole_diameter / 2.0],
            [-x, n, self.flavor_tube_hole_dia / 2.0],
            [x, n, self.flavor_tube_hole_dia / 2.0],
        ];
        if include_signal {
            let half = (self.signal_lane_width - self.signal_lane_depth) / 2.0;
            for x in [-half, half] {
                rows.push([x, ribbon, self.signal_lane_depth / 2.0]);
            }
        }
        rows
    }
    pub fn ribbon_end_station(&self) -> f64 {
        let angle = self._path_total_rot
            - ((self.display_ribbon_join_s - self.gn_tip_straight_len)
                / (self.gn_bend1_r + self.signal_lane_center_n))
                .asin();
        (angle - crate::JOINT_ANGLE) * crate::water_radius()
    }
    pub fn bundle_stations(&self, s0: f64, s1: f64) -> Vec<f64> {
        let n = (((s1 - s0) / 2.0).ceil() as usize).max(2);
        (0..=n)
            .map(|i| s0 + (s1 - s0) * i as f64 / n as f64)
            .collect()
    }
    pub fn tip_frame(&self) -> [[f64; 3]; 3] {
        let ta = self._tan_after_bend2[0];
        let tb = self._tan_after_bend2[1];
        [
            [
                0.0,
                self.soda_faucet_tube_y - self._path_p5[0],
                self.zone5_z_top + self._path_p5[1],
            ],
            [0.0, ta, -tb],
            [0.0, tb, ta],
        ]
    }
    pub fn vent_frame(&self) -> ([f64; 3], [f64; 3], f64) {
        let station = crate::drip_hole_s();
        let angle = self.split_junction_rot + station / self.gn_bend1_r;
        let origin = crate::station_point(station, 0.0, self.tube_shell_center_y);
        let offset = self.tube_shell_center_y + self.soda_faucet_hole_diameter / 2.0
            - self.vent_outlet_reach;
        (origin, [0.0, -angle.cos(), -angle.sin()], offset)
    }
    pub fn lower_bundle(&self) -> Value {
        json!({"signal_lane_z":[self.signal_lane_bottom_z,self.lower_signal_stations().last().unwrap()[0]],"signal_lower_exit":[self.signal_lower_exit_x,self.signal_lower_exit_y],"signal_lower_exit_angle":self.signal_lower_exit_angle,"signal_lane_width":self.signal_lane_width,"signal_lane_depth":self.signal_lane_depth,"lower_opening_sections":self.lower_heights().iter().map(|z|json!({"z":z,"circles":self.lower_circles(*z)})).collect::<Vec<_>>(),"bundle_land_bottom_z":self.zone3_z_bottom-self.bundle_land_below,"bundle_land_above":self.bundle_land_above})
    }
    pub fn lever_outline(&self) -> Result<Vec<[f64; 2]>> {
        crate::geos::lever_outline(self)
    }
    pub fn display_ribbon_frames(&self, width: f64, depth: f64, top_n: f64) -> Result<Vec<Value>> {
        let [origin, along, outward] = self.tip_frame();
        let mut frames: Vec<([f64; 3], [f64; 3])> = vec![];
        let natural = |s: f64| {
            let r = self.gn_bend1_r + self.signal_lane_center_n;
            let square = (r * r - (s - self.gn_tip_straight_len).powi(2)).sqrt();
            (
                square - self.gn_bend1_r,
                -(s - self.gn_tip_straight_len) / square,
            )
        };
        let add = |frames: &mut Vec<([f64; 3], [f64; 3])>, p: [f64; 3], t: [f64; 3]| {
            if frames.last().is_none_or(|(q, _)| dist(*q, p) >= 1e-8) {
                frames.push((p, t));
            }
        };
        for s in [
            self.display_ribbon_reference_start_s,
            (self.display_ribbon_reference_start_s + self.display_ribbon_join_s) / 2.0,
            self.display_ribbon_join_s,
        ] {
            let (n, slope) = natural(s);
            add(&mut frames, [0.0, s, n], [0.0, -1.0, -slope]);
        }
        let side = self.display_ribbon_side_x.signum();
        let side_x = self.display_ribbon_side_x.abs();
        let r = self.display_ribbon_side_radius;
        let angle = (1.0 - side_x / (2.0 * r)).acos();
        for phase in 0..2 {
            for step in 0..13 {
                let u = angle * step as f64 / 12.0;
                let turn = if phase == 0 { u } else { angle - u };
                let (x, s) = if phase == 0 {
                    (
                        r * (1.0 - u.cos()),
                        self.display_ribbon_join_s - r * u.sin(),
                    )
                } else {
                    (
                        r * (1.0 - 2.0 * angle.cos() + turn.cos()),
                        self.display_ribbon_join_s - r * (2.0 * angle.sin() - turn.sin()),
                    )
                };
                let (dx, ds) = (turn.sin(), -turn.cos());
                let (mut n, slope) = natural(s);
                let fraction = x / side_x;
                n += -self.display_ribbon_side_drop * fraction.powi(4)
                    + self.display_ribbon_side_lift * 4.0 * fraction * (1.0 - fraction);
                let dn = slope * ds
                    - 4.0 * self.display_ribbon_side_drop * fraction.powi(3) * dx / side_x
                    + 4.0 * self.display_ribbon_side_lift * (1.0 - 2.0 * fraction) * dx / side_x;
                add(&mut frames, [side * x, s, n], [side * dx, ds, dn]);
            }
        }
        let ([x, s0, n0], [_, ds, dn]) = *frames.last().unwrap();
        let run_in = 3.0;
        let m0 = run_in * dn / -ds;
        for step in 1..13 {
            let t = step as f64 / 12.0;
            let n = (2.0 * t.powi(3) - 3.0 * t * t + 1.0) * n0
                + (t.powi(3) - 2.0 * t * t + t) * m0
                + (-2.0 * t.powi(3) + 3.0 * t * t) * self.display_ribbon_side_run_n;
            let dn = (6.0 * t * t - 6.0 * t) * n0
                + (3.0 * t * t - 4.0 * t + 1.0) * m0
                + (-6.0 * t * t + 6.0 * t) * self.display_ribbon_side_run_n;
            add(&mut frames, [x, s0 - run_in * t, n], [0.0, -run_in, dn]);
        }
        let side_start = s0 - run_in;
        let pre = self.display_ribbon_terminal_s + self.display_wire_bend_radius;
        for step in 1..9 {
            add(
                &mut frames,
                [
                    x,
                    side_start + (pre - side_start) * step as f64 / 8.0,
                    self.display_ribbon_side_run_n,
                ],
                [0.0, -1.0, 0.0],
            );
        }
        let (mut s, mut n) = (0.0, 0.0);
        for step in 1..17 {
            let t = std::f64::consts::PI / 2.0 * step as f64 / 16.0;
            s = pre - self.display_wire_bend_radius * t.sin();
            n = self.display_ribbon_side_run_n + self.display_wire_bend_radius * (1.0 - t.cos());
            add(&mut frames, [x, s, n], [0.0, -t.cos(), t.sin()]);
        }
        if top_n <= n {
            bail!("ribbon termination must reach above its smooth PCB-side bend");
        }
        add(&mut frames, [x, s, top_n], [0.0, 0.0, 1.0]);
        Ok(frames
            .into_iter()
            .map(|([x, s, n], [dx, ds, dn])| {
                let mut center = [0.0; 3];
                let mut tangent = [0.0; 3];
                let mut cross = [0.0; 3];
                for i in 0..3 {
                    let q = if i == 0 { x } else { 0.0 };
                    center[i] = origin[i] + q + along[i] * s + outward[i] * n;
                    let q = if i == 0 { dx } else { 0.0 };
                    tangent[i] = q + along[i] * ds + outward[i] * dn;
                    let q = if i == 0 { -ds } else { 0.0 };
                    cross[i] = q + along[i] * dx;
                }
                if cross.iter().map(|v| v * v).sum::<f64>().sqrt() < 1e-8 {
                    cross = [1.0, 0.0, 0.0];
                }
                json!({"origin":center,"xdir":cross,"normal":tangent,"rect":[width,depth]})
            })
            .collect())
    }
}
pub fn dist(a: [f64; 3], b: [f64; 3]) -> f64 {
    (a[0] - b[0]).hypot(a[1] - b[1]).hypot(a[2] - b[2])
}

impl Dimensions {
    pub fn bounds(&self) -> Value {
        let g = |v: f64| hsm_documents::format_number(v, "g").unwrap();
        let rows: Vec<_> = self
            .base_pod_centers
            .iter()
            .map(|xy| {
                let stock = xy[0].hypot(xy[1])
                    - self.westbrass_bore_diameter / 2.0
                    - self.base_insert_outer_dia / 2.0;
                json!([
                    stock >= self.wall_thickness_min,
                    format!(
                        "insert at ({}, {}) has {:.4} mm to the donor cavity",
                        g(xy[0]),
                        g(xy[1]),
                        stock
                    )
                ])
            })
            .collect();
        json!([
         {"id":"faucet-base-insert-wall","label":"The base inserts keep a full wall to the Westbrass cavity","target":format!("at least {} mm",g(self.wall_thickness_min)),"readings":rows},
         {"id":"faucet-base-screw-seat","label":"The hidden screw head bears on a full printed wall","target":format!("at least {} mm",g(self.wall_thickness_min)),"readings":[[self.base_plate_seat_thickness>=self.wall_thickness_min-1e-9,format!("the {} mm plate and {} mm pedestal retain {} mm above the {} mm counterbore",g(self.above_counter_plate_thickness),g(self.base_pedestal_height),g(self.base_plate_seat_thickness),g(self.base_screw_counterbore_depth))]]},
         {"id":"faucet-neck-joint-walls","label":"The circular gooseneck joint carries two full walls","target":format!("socket and plug at least {} mm",g(self.wall_thickness_min)),"readings":[[self.split_socket_wall>=self.wall_thickness_min,format!("socket wall {} mm",g(self.split_socket_wall))],[self._neck_plug_min_wall>=self.wall_thickness_min-1e-9,format!("plug wall {:.4} mm around all tube and cable passages",self._neck_plug_min_wall)]]}
        ])
    }
}
pub fn print_height(path: &std::path::Path, rotation: f64) -> Result<f64> {
    let data = std::fs::read(path)?;
    let mut lo = f64::INFINITY;
    let mut hi = f64::NEG_INFINITY;
    for facet in data
        .get(84..)
        .context("binary STL header")?
        .chunks_exact(50)
    {
        for vertex in facet[12..48].chunks_exact(12) {
            let y = f32::from_le_bytes(vertex[4..8].try_into().unwrap()) as f64;
            let z = f32::from_le_bytes(vertex[8..12].try_into().unwrap()) as f64;
            let h = z * rotation.cos() - y * rotation.sin();
            lo = lo.min(h);
            hi = hi.max(h);
        }
    }
    if !lo.is_finite() {
        bail!("STL has no corners");
    }
    Ok(hi - lo)
}
pub fn dispatch(request: &Value) -> Result<Value> {
    let d = Dimensions::new(request["slip"].as_f64().unwrap_or(0.15));
    let args = request["args"].as_array().cloned().unwrap_or_default();
    let f = |i: usize, default: f64| args.get(i).and_then(Value::as_f64).unwrap_or(default);
    Ok(match request["fn"].as_str().unwrap_or("datums") {
        "datums" => json!({"datums":d,"bounds":d.bounds()}),
        "numbers" => d.numbers(&request["color"])?,
        "interface_variables" => crate::formatted(&[
            ("FLAVOR_TUBE_X_OFFSET", d.flavor_tube_x_offset, ".4g", " mm"),
            ("FLAVOR_TUBE_HOLE_DIA", d.flavor_tube_hole_dia, ".4g", " mm"),
            ("PILL_LENGTH_X", d.pill_length_x, ".4g", " mm"),
            ("PILL_WIDTH_Y", d.pill_width_y, ".4g", " mm"),
            ("FLAVOR_TUBE_DEPTH", d.flavor_tube_depth, ".5g", " mm"),
            (
                "DISPLAY_HOUSING_OVERHANG",
                (d.display_housing_width - d.display_pcb_width) / 2.0,
                ".4g",
                " mm",
            ),
            (
                "DISPLAY_PCB_BOTTOM_Z",
                crate::interface(d.display_cover_slip)["display_pcb_bottom_z"]
                    .as_f64()
                    .unwrap(),
                ".4g",
                " mm",
            ),
            ("DISPLAY_PCB_TOP_Z", d.display_pcb_top_z, ".4g", " mm"),
        ]),
        "lower_bundle_numbers" => d.lower_bundle(),
        "_bend2_point" => json!(d.bend2_point(f(0, 0.0))),
        "_lower_signal_stations" => json!(d.lower_signal_stations()),
        "_lower_signal_profiles" => json!(d.lower_signal_profiles(
            f(0, 0.0),
            f(1, 0.0),
            args.get(2).and_then(Value::as_bool).unwrap_or(false),
            f(3, 0.0),
            f(4, 0.0)
        )),
        "_lower_opening_heights" => json!(d.lower_heights()),
        "_lower_opening_circles" => json!(d.lower_circles(f(0, 0.0))),
        "_tube_shell_inner_circles" => json!(d.tube_circles(
            request["include_signal"].as_bool().unwrap_or(true),
            request["station"].as_f64().unwrap_or(0.0)
        )),
        "_ribbon_end_station" => json!(d.ribbon_end_station()),
        "_bundle_stations" => json!(d.bundle_stations(f(0, 0.0), f(1, 0.0))),
        "_tip_frame_data" => json!(d.tip_frame()),
        "_vent_outlet_frame" => {
            let (o, n, t) = d.vent_frame();
            json!([o, n, t])
        }
        "_display_ribbon_frames" => {
            json!(d.display_ribbon_frames(f(0, 0.0), f(1, 0.0), f(2, 0.0))?)
        }
        "_lever_outline" => json!(d.lever_outline()?),
        "print_height" => json!(print_height(
            std::path::Path::new(request["path"].as_str().context("STL path")?),
            f(0, 0.0)
        )?),
        "variables" => {
            let mut heights = serde_json::Map::new();
            if let Some(root) = request["directory"].as_str() {
                for (name, angle) in [
                    ("faucet-shell-base.stl", d.print_base_build_rot),
                    ("faucet-shell-tip.stl", d.print_tip_build_rot),
                ] {
                    heights.insert(
                        name.to_owned(),
                        json!(print_height(&std::path::Path::new(root).join(name), angle)?),
                    );
                }
            }
            d.variables(&Value::Object(heights))?
        }
        name => bail!("unknown shell scalar operation {name}"),
    })
}

impl Dimensions {
    pub fn numbers(&self, color: &Value) -> Result<Value> {
        let paths = crate::constants();
        let snap = crate::covers::snap();
        let end = crate::converge_start_s() + crate::CONVERGE_LENGTH;
        let [_, drain_x, drain_t] = crate::station_plane(crate::drain_cut_s(), 0.0);
        let (vent_origin, vent_normal, vent_offset) = self.vent_frame();
        let passage_section = |station: f64| {
            let [origin, xdir, normal] = crate::station_plane(station, 0.0);
            json!({"origin":origin,"xdir":xdir,"normal":normal,"circles":self.tube_circles(true,station)})
        };
        let mut out = Value::Object(serde_json::Map::new());
        out["name"] = json!(("faucet-shell".to_string()));
        out["color"] = json!((color.clone()));
        out["zone5_z_top"] = json!((self.zone5_z_top));
        out["zone5_z_bottom"] = json!((self.zone5_z_bottom));
        out["soda_faucet_tube_y"] = json!((self.soda_faucet_tube_y));
        out["gn_bend1_z_start"] = json!((self.gn_bend1_z_start));
        out["gn_bend1_r"] = json!((self.gn_bend1_r));
        out["path_total_rot"] = json!((self._path_total_rot));
        out["gn_tip_straight_len"] = json!((self.gn_tip_straight_len));
        out["joint_angle"] = json!((paths["JOINT_ANGLE"].as_f64().unwrap()));
        out["water_radius"] = json!((paths["WATER_RADIUS"].as_f64().unwrap()));
        out["tube_shell_outer_r"] = json!((self.tube_shell_outer_r));
        out["tube_shell_center_y"] = json!((self.tube_shell_center_y));
        out["shell_outer_r"] = json!((self.shell_outer_r));
        out["wall_thickness_min"] = json!((self.wall_thickness_min));
        out["lower_outer_sections"] = json!((self.lower_outer_sections.clone()));
        out["lower_neck_z"] = json!((self.lower_neck_z));
        out["neck_land_overrun"] = json!((self.neck_land_overrun));
        out["split_junction_rot"] = json!((self.split_junction_rot));
        out["path_socket_start_rot"] = json!((self._path_socket_start_rot));
        out["split_socket_shrink"] = json!((self.split_socket_shrink));
        out["path_plug_start_rot"] = json!((self._path_plug_start_rot));
        out["split_plug_shrink"] = json!((self.split_plug_shrink));
        out["zone1_z_bottom"] = json!((self.zone1_z_bottom));
        out["zone1_height"] = json!((self.zone1_height));
        out["zone2_bore_z_bottom"] = json!((self.zone2_bore_z_bottom));
        out["zone2_z_bottom"] = json!((self.zone2_z_bottom));
        out["zone2_z_top"] = json!((self.zone2_z_top));
        out["zone2_height"] = json!((self.zone2_height));
        out["zone3_z_bottom"] = json!((self.zone3_z_bottom));
        out["westbrass_bore_x"] = json!((self.westbrass_bore_x));
        out["westbrass_bore_y"] = json!((self.westbrass_bore_y));
        out["westbrass_bore_diameter"] = json!((self.westbrass_bore_diameter));
        out["westbrass_bore_rect_short_x"] = json!((self.westbrass_bore_rect_short_x));
        out["westbrass_bore_rect_long_y"] = json!((self.westbrass_bore_rect_long_y));
        out["cove_r"] = json!((self.cove_r));
        out["bore_overrun"] = json!((self.bore_overrun));
        out["shell_arch_bore_inner_x"] = json!((self.shell_arch_bore_inner_x));
        out["shell_arch_bore_outer_x"] = json!((self.shell_arch_bore_outer_x));
        out["shell_arch_bore_z_foot_top"] = json!((self.shell_arch_bore_z_foot_top));
        out["shell_arch_bore_z_peak"] = json!((self.shell_arch_bore_z_peak));
        out["fill_y_min"] = json!((self.fill_y_min));
        out["flavor_pill_center"] = json!((self.flavor_pill_center.clone()));
        out["pill_length_x"] = json!((self.pill_length_x));
        out["pill_width_y"] = json!((self.pill_width_y));
        out["flavor_pill_y_minus_edge"] = json!((self.flavor_pill_y_minus_edge));
        out["base_pod_centers"] = json!((self.base_pod_centers.clone()));
        out["base_pod_z_bottom"] = json!((self.base_pod_z_bottom));
        out["base_pod_hole_dia"] = json!((self.base_pod_hole_dia));
        out["base_pod_hole_depth"] = json!((self.base_pod_hole_depth));
        out["base_insert_bottom_z"] = json!((self.base_insert_bottom_z));
        out["base_pod_insert_dia"] = json!((self.base_pod_insert_dia));
        out["base_pod_insert_depth"] = json!((self.base_pod_insert_depth));
        out["lever_outline"] = json!((self.lever_outline()?));
        out["lever_clearance_x_half"] = json!((self.lever_clearance_x_half));
        out["lever_clearance_y_back"] = json!((self.lever_clearance_y_back));
        out["lever_insertion_front_y"] = json!((self.lever_insertion_front_y));
        out["lever_rest_top_z"] = json!((self.lever_rest_top_z));
        out["back_arch_r"] = json!((self.back_arch_r));
        out["back_arch_center_z"] = json!((self.back_arch_center_z));
        out["zone45_front_y"] = json!((self.zone45_front_y));
        out["drain_relief"] = json!(
            (json!({"origin":(crate::tube_arc_point(paths["DRAIN_CUT_S"].as_f64().unwrap(),"drain",1.0)),"xdir":(drain_x),"normal":(drain_t)}))
        );
        out["drain_relief_lead"] = json!((self.drain_relief_lead));
        out["drain_tube_hole_dia"] = json!(
            (crate::interface(self.display_cover_slip)["drain_tube_hole_dia"]
                .as_f64()
                .unwrap())
        );
        out["drip_end_clearance"] = json!((paths["DRIP_END_CLEARANCE_MM"].as_f64().unwrap()));
        out["vent_outlet"] = json!((json!({"origin":(vent_origin),"normal":(vent_normal)})));
        out["vent_outlet_offset"] = json!((vent_offset));
        out["drip_hole_diameter"] = json!((paths["DRIP_HOLE_DIAMETER"].as_f64().unwrap()));
        out["dispense_face_thickness"] = json!((self.dispense_face_thickness));
        out["display_s_top"] = json!((self.display_s_top));
        out["display_neck_outer_r"] = json!((self.display_neck_outer_r));
        out["display_seat_reference_n"] = json!((self.display_seat_reference_n));
        out["display_pocket_top_n"] =
            json!((self.display_cover_top_n + self.display_pocket_overrun));
        out["display_channel_half_width"] = json!((self.display_channel_half_width));
        out["display_channel_top_n"] =
            json!((self.display_seat_reference_n + self.display_channel_overlap));
        out["display_foot_centers"] = json!((self.display_foot_centers.clone()));
        out["display_foot_pad_width"] = json!((self.display_foot_pad_width));
        out["display_foot_pad_depth"] = json!((self.display_foot_pad_depth));
        out["display_feet_n"] = json!((self.display_feet_n));
        out["display_groove_half_x"] =
            json!((self.display_neck_outer_r + self.display_groove_reach));
        out["display_groove_core_r"] = json!(
            (self.display_neck_outer_r
                - (self.display_neck_outer_r - self.display_clip_groove_radius))
        );
        out["display_clip_s_bottom"] = json!((self.display_clip_s_bottom));
        out["display_clip_s_top"] = json!((self.display_clip_s_top));
        out["display_clip_bottom_n"] = json!((self.display_clip_bottom_n));
        out["display_clip_top_n"] = json!((self.display_clip_top_n));
        out["snap_end_slip"] = json!((snap["END_SLIP"].as_f64().unwrap()));
        out["snap_bearing_slip"] = json!((snap["BEARING_SLIP"].as_f64().unwrap()));
        out["passage_sections"] = json!(
            ({
                let mut out5 = Vec::new();
                for row5_0 in
                    (self.bundle_stations(paths["CONVERGE_START_S"].as_f64().unwrap(), end)).iter()
                {
                    let station = row5_0.clone();
                    out5.push(passage_section(station));
                }
                out5
            })
        );
        out["converge_start_s"] = json!((paths["CONVERGE_START_S"].as_f64().unwrap()));
        out["converge_length"] = json!((paths["CONVERGE_LENGTH"].as_f64().unwrap()));
        out["ribbon_end_s"] = json!((self.ribbon_end_station()));
        out["beverage_lead"] = json!((self.beverage_lead));
        out["beverage_circles"] = json!((self.tube_circles(false, end)));

        out.as_object_mut()
            .unwrap()
            .extend(self.lower_bundle().as_object().unwrap().clone());
        Ok(out)
    }
    pub fn variables(&self, heights: &Value) -> Result<Value> {
        let mut variables = serde_json::Map::new();
        variables.insert(
            "DISPENSE_FACE_T".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.dispense_face_thickness, "g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "NECK_DIAMETER".to_owned(),
            json!(
                [
                    hsm_documents::format_number((2.0 * self.tube_shell_outer_r), ".3f")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "FOOT_WIDTH".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.foot_width, "g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "FOOT_DEPTH".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.foot_depth, "g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "PLATE_T".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.above_counter_plate_thickness, "g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "PEDESTAL_H".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.base_pedestal_height, "g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "BASE_INSERT_Z".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.base_insert_bottom_z, "g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "BASE_INSERT_L".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.base_insert_length, "g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "BASE_CBORE_D".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.base_pod_counterbore_dia, "g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "BASE_CBORE_DEPTH".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.base_screw_counterbore_depth, "g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "BASE_SCREW_L".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.base_screw_length, "g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "BASE_X".to_owned(),
            json!([hsm_documents::format_number(self.base_pod_center_x, "g")?].concat()),
        );
        variables.insert(
            "BASE_Y".to_owned(),
            json!([hsm_documents::format_number(self.base_pod_center_y, "g")?].concat()),
        );
        variables.insert(
            "BASE_FRONT_Y".to_owned(),
            json!(
                [hsm_documents::format_number(
                    self.base_pod_front_center_y,
                    "g"
                )?]
                .concat()
            ),
        );
        variables.insert(
            "BORE_CLEAR".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.bore_clearance, ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "WESTBRASS_BORE_D".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.westbrass_bore_diameter, ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "WESTBRASS_OD".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.westbrass_rect_long_y, ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "WESTBRASS_RECT_LONG".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.westbrass_rect_long_y, ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "WESTBRASS_RECT_SHORT".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.westbrass_rect_short_x, ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "WESTBRASS_CYL_TOP_Z".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.zone1_z_top, ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "BORE_COVE_Z".to_owned(),
            json!(
                [
                    hsm_documents::format_number((self.zone2_bore_z_bottom + self.cove_r), ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "PILL_L".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.pill_length_x, ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "PILL_W".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.pill_width_y, ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "FLAVOR_TUBE_OD".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.flavor_tube_od, ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "WESTBRASS_RECT_LONG_HALF".to_owned(),
            json!(
                [
                    hsm_documents::format_number((self.westbrass_rect_long_y / 2.0), ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "LEVER_REST_TOP_Z".to_owned(),
            json!(
                [
                    hsm_documents::format_number((self.zone2_z_top + 13.0), ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "FLAVOR_TUBE_Y".to_owned(),
            json!(
                [
                    hsm_documents::format_number((self.flavor_pill_center.clone())[1], ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "FLAVOR_PILL_Y_MINUS".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.flavor_pill_y_minus_edge, ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "BASE_POD_FRONT_CENTER_Y".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.base_pod_front_center_y, ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "SHELL_OUTER_R".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.shell_outer_r, ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "SHOW_WALL".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.show_wall, ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "PRINT_LAYER".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.print_layer_height, ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "PRINT_BEAD".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.print_bead_width, ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "SODA_FAUCET_HOLE_D".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.soda_faucet_hole_diameter, ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "WALL_MIN".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.wall_thickness_min, ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "ZONE1_HEIGHT".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.zone1_height, ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "ZONE2_HEIGHT".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.zone2_height, ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "ZONE4_HEIGHT".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.zone4_height, ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "ZONE5_HEIGHT".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.zone5_height, ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "ZONE5_WALL".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.zone5_wall, ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "WESTBRASS_BORE_FARTHEST".to_owned(),
            json!(
                [
                    hsm_documents::format_number(
                        self._westbrass_bore_farthest_from_shell_center,
                        ".4g"
                    )?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "PILL_FARTHEST".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self._pill_farthest_from_shell_center, ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "WESTBRASS_BORE_RECT_LONG".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.westbrass_bore_rect_long_y, ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "WESTBRASS_BORE_RECT_SHORT".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.westbrass_bore_rect_short_x, ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "ZONE2_BORE_Z_BOTTOM".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.zone2_bore_z_bottom, ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "SHELL_OUTER_LIP".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.shell_outer_lip, ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "ZONE1_OUTER_Z_TOP".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.zone1_outer_z_top, ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "SHELL_RECT_X_HALF".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.shell_rect_x_half, ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "SHELL_RECT_Y_MAX".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.shell_rect_y_max, ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "SHELL_RECT_Y_MIN".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.shell_rect_y_min, ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "ZONE3_Z_BOTTOM".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.zone3_z_bottom, ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "WING_INNER_X".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.wing_inner_x, ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "SHELL_ARCH_BORE_INNER_X".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.shell_arch_bore_inner_x, ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "SHELL_ARCH_BORE_OUTER_X".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.shell_arch_bore_outer_x, ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "SHELL_ARCH_BORE_Z_FOOT_TOP".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.shell_arch_bore_z_foot_top, ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "SHELL_ARCH_BORE_Z_PEAK".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.shell_arch_bore_z_peak, ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "SHELL_ARCH_Z_FOOT_TOP".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.shell_arch_z_foot_top, ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "SHELL_ARCH_Z_PEAK".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.shell_arch_z_peak, ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "SODA_FAUCET_TUBE_OD".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.soda_faucet_tube_od, ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "SODA_FAUCET_TUBE_Y".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.soda_faucet_tube_y, ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "TUBE_SHELL_SODA_R".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.tube_shell_soda_r_outer, ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "FLAVOR_POST_BEND_Y".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.flavor_tube_post_bend_y, ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "FILL_Y_MIN".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.fill_y_min, ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "FILL_X_THICKNESS".to_owned(),
            json!(
                [
                    hsm_documents::format_number((2.0 * self.wing_inner_x), ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "PILL_STRAIGHT_INNER".to_owned(),
            json!(
                [
                    hsm_documents::format_number((self.pill_length_x - self.pill_width_y), ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "FLAVOR_OFFSET_Y".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.flavor_offset_y_from_water, ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "ZONE5_Z_BOTTOM".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.zone5_z_bottom, ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "ZONE5_Z_TOP".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.zone5_z_top, ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "GN_BEND1_Z_MID".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.gn_bend1_z_mid, ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "GN_BEND1_Z_START".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.gn_bend1_z_start, ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "GN_BEND2_SWEEP_DEG".to_owned(),
            json!(
                [
                    hsm_documents::format_number(
                        (self.gn_bend2_sweep_rad) * (180.0 / std::f64::consts::PI),
                        ".0f"
                    )?,
                    String::from("°")
                ]
                .concat()
            ),
        );
        variables.insert(
            "GN_TOTAL_ROT".to_owned(),
            json!(
                [
                    hsm_documents::format_number(
                        (self._path_total_rot) * (180.0 / std::f64::consts::PI),
                        ".0f"
                    )?,
                    String::from("°")
                ]
                .concat()
            ),
        );
        variables.insert(
            "SPLIT_JUNCTION_ROT".to_owned(),
            json!(
                [
                    hsm_documents::format_number(
                        (self.split_junction_rot) * (180.0 / std::f64::consts::PI),
                        ".0f"
                    )?,
                    String::from("°")
                ]
                .concat()
            ),
        );
        variables.insert(
            "SPLIT_JUNCTION_Y".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.split_junction_y, ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "SPLIT_JUNCTION_Z".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.split_junction_z, ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "SPLIT_OVERLAP".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.split_socket_overlap_len, ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "SPLIT_SOCKET_WALL".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.split_socket_wall, ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "SPLIT_PLUG_WALL".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.split_plug_wall, ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "SPLIT_SLIP".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.split_slip, ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "DISPLAY_INSTALL_LIFT".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.display_cartridge_lift_n, "g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "PRINT_TILT".to_owned(),
            json!(
                [
                    hsm_documents::format_number(
                        (self.print_base_tilt_rad) * (180.0 / std::f64::consts::PI),
                        ".0f"
                    )?,
                    String::from("°")
                ]
                .concat()
            ),
        );
        variables.insert(
            "MAX_PRINT_OVERHANG".to_owned(),
            json!(
                [
                    hsm_documents::format_number(
                        (self.max_print_overhang_rad) * (180.0 / std::f64::consts::PI),
                        ".0f"
                    )?,
                    String::from("°")
                ]
                .concat()
            ),
        );
        variables.insert(
            "BASE_PRINT_HEIGHT".to_owned(),
            json!(
                [
                    hsm_documents::format_number(
                        heights["faucet-shell-base.stl"].as_f64().unwrap_or(0.0),
                        ".1f"
                    )?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "TIP_PRINT_HEIGHT".to_owned(),
            json!(
                [
                    hsm_documents::format_number(
                        heights["faucet-shell-tip.stl"].as_f64().unwrap_or(0.0),
                        ".1f"
                    )?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "BACK_ARCH_DY".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self._back_arch_dy, ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "Z5_Y_MIN".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self._z5_y_min, ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "ZONE45_Z_TOP".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.zone45_z_top, ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        variables.insert(
            "ZONE45_Z_BOT_FRONT".to_owned(),
            json!(
                [
                    hsm_documents::format_number(self.zone45_z_bottom_at_front, ".4g")?,
                    String::from(" mm")
                ]
                .concat()
            ),
        );
        Ok(Value::Object(variables))
    }
}
