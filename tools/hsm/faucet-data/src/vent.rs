//! Retained ASSE gland and tube-pack dimensions and independent scalar readings.
#![allow(non_snake_case, unused_parens)]
use anyhow::{Result, bail, ensure};
use serde::Serialize;
use serde_json::{Value, json};
#[derive(Serialize)]
struct Dimensions {
    SODA_OD: f64,
    FLAVOR_OD: f64,
    DRAIN_OD: f64,
    SEAL_WEB: f64,
    SHELL_CENTER_N: f64,
    NECK_OD: f64,
    WATER_BEND_RADIUS: f64,
    DRAIN_N: f64,
    _sf: f64,
    _df: f64,
    FLAVOR_N: f64,
    FLAVOR_X: f64,
    WIRE_N: f64,
    WIRE_X: Vec<f64>,
    WIRE_BORE: f64,
    TUBE_DIAMETRIC_INTERFERENCE: f64,
    BORE_LEAD_RADIAL: f64,
    BORE_LEAD_DEPTH: f64,
    BODY_OD: f64,
    BODY_LENGTH: f64,
    FLANGE_OD: f64,
    FLANGE_LENGTH: f64,
    BUNG_LENGTH: f64,
    KEEPER_ID: f64,
    KEEPER_LENGTH: f64,
    GROOVE_ID: f64,
    GROOVE_LENGTH: f64,
    BODY_SEAT_ID: f64,
    STOP_ID: f64,
    UPSTREAM_STOP_ID: f64,
    STOP_LENGTH: f64,
    KEEPER_LEAD_RADIAL: f64,
    KEEPER_LEAD_LENGTH: f64,
    GLAND_LENGTH: f64,
    BUNG_SEATED_Z: f64,
    BODY_MID_Z: f64,
    TOOL_OD: f64,
    TOOL_ID: f64,
    TOOL_SLOT_WIDTH: f64,
    TOOL_ARC_LENGTH: f64,
    TOOL_HANDLE_OD: f64,
    TOOL_HANDLE_LENGTH: f64,
    STL_LINEAR_TOLERANCE: f64,
    STL_ANGULAR_TOLERANCE: f64,
}
impl Dimensions {
    fn new() -> Self {
        let paths = crate::constants();
        let SODA_OD: f64 = paths["WATER_OD"].as_f64().unwrap();
        let FLAVOR_OD: f64 = paths["FLAVOR_OD"].as_f64().unwrap();
        let DRAIN_OD: f64 = paths["DRAIN_OD"].as_f64().unwrap();
        let SEAL_WEB: f64 = paths["SEAL_WEB"].as_f64().unwrap();
        let SHELL_CENTER_N: f64 = paths["SHELL_CENTER_N"].as_f64().unwrap();
        let NECK_OD: f64 = (2.0 * paths["SHELL_RADIUS"].as_f64().unwrap());
        let WATER_BEND_RADIUS: f64 = paths["WATER_RADIUS"].as_f64().unwrap();
        let DRAIN_N: f64 = (((SODA_OD + DRAIN_OD) / 2.0) + SEAL_WEB);
        let _sf: f64 = (((SODA_OD + FLAVOR_OD) / 2.0) + SEAL_WEB);
        let _df: f64 = (((DRAIN_OD + FLAVOR_OD) / 2.0) + SEAL_WEB);
        let FLAVOR_N: f64 =
            ((((_sf).powi(2) - (_df).powi(2)) + (DRAIN_N).powi(2)) / (2.0 * DRAIN_N));
        let FLAVOR_X: f64 = ((_sf).powi(2) - (FLAVOR_N).powi(2)).sqrt();
        let WIRE_N: f64 = (((DRAIN_N + (DRAIN_OD / 2.0)) + SEAL_WEB) + 0.65);
        let WIRE_X: Vec<f64> = vec![-(3.3), -(1.1), 1.1, 3.3];
        let WIRE_BORE: f64 = 1.05;
        let TUBE_DIAMETRIC_INTERFERENCE: f64 = 0.3;
        let BORE_LEAD_RADIAL: f64 = 0.1;
        let BORE_LEAD_DEPTH: f64 = 0.2;
        let BODY_OD: f64 = 22.4;
        let BODY_LENGTH: f64 = 4.0;
        let FLANGE_OD: f64 = 23.0;
        let FLANGE_LENGTH: f64 = 0.8;
        let BUNG_LENGTH: f64 = (BODY_LENGTH + FLANGE_LENGTH);
        let KEEPER_ID: f64 = 22.0;
        let KEEPER_LENGTH: f64 = 1.2;
        let GROOVE_ID: f64 = 22.8;
        let GROOVE_LENGTH: f64 = 0.9;
        let BODY_SEAT_ID: f64 = 22.0;
        let STOP_ID: f64 = 20.0;
        let UPSTREAM_STOP_ID: f64 = 22.0;
        let STOP_LENGTH: f64 = 1.2;
        let KEEPER_LEAD_RADIAL: f64 = 0.3;
        let KEEPER_LEAD_LENGTH: f64 = 0.3;
        let GLAND_LENGTH: f64 = (((KEEPER_LENGTH + GROOVE_LENGTH) + BODY_LENGTH) + STOP_LENGTH);
        let BUNG_SEATED_Z: f64 = ((KEEPER_LENGTH + GROOVE_LENGTH) - FLANGE_LENGTH);
        let BODY_MID_Z: f64 = ((KEEPER_LENGTH + GROOVE_LENGTH) + (BODY_LENGTH / 2.0));
        let TOOL_OD: f64 = 21.5;
        let TOOL_ID: f64 = 19.7;
        let TOOL_SLOT_WIDTH: f64 = 19.0;
        let TOOL_ARC_LENGTH: f64 = 95.0;
        let TOOL_HANDLE_OD: f64 = 32.0;
        let TOOL_HANDLE_LENGTH: f64 = 4.0;
        let STL_LINEAR_TOLERANCE: f64 = 0.005;
        let STL_ANGULAR_TOLERANCE: f64 = 0.04;
        Self {
            SODA_OD,
            FLAVOR_OD,
            DRAIN_OD,
            SEAL_WEB,
            SHELL_CENTER_N,
            NECK_OD,
            WATER_BEND_RADIUS,
            DRAIN_N,
            _sf,
            _df,
            FLAVOR_N,
            FLAVOR_X,
            WIRE_N,
            WIRE_X,
            WIRE_BORE,
            TUBE_DIAMETRIC_INTERFERENCE,
            BORE_LEAD_RADIAL,
            BORE_LEAD_DEPTH,
            BODY_OD,
            BODY_LENGTH,
            FLANGE_OD,
            FLANGE_LENGTH,
            BUNG_LENGTH,
            KEEPER_ID,
            KEEPER_LENGTH,
            GROOVE_ID,
            GROOVE_LENGTH,
            BODY_SEAT_ID,
            STOP_ID,
            UPSTREAM_STOP_ID,
            STOP_LENGTH,
            KEEPER_LEAD_RADIAL,
            KEEPER_LEAD_LENGTH,
            GLAND_LENGTH,
            BUNG_SEATED_Z,
            BODY_MID_Z,
            TOOL_OD,
            TOOL_ID,
            TOOL_SLOT_WIDTH,
            TOOL_ARC_LENGTH,
            TOOL_HANDLE_OD,
            TOOL_HANDLE_LENGTH,
            STL_LINEAR_TOLERANCE,
            STL_ANGULAR_TOLERANCE,
        }
    }
}
impl Dimensions {
    fn tubes(&self, upstream: bool) -> Vec<(String, f64, f64, f64)> {
        let mut t = vec![
            ("S".into(), 0.0, 0.0, self.SODA_OD),
            ("F1".into(), -self.FLAVOR_X, self.FLAVOR_N, self.FLAVOR_OD),
            ("F2".into(), self.FLAVOR_X, self.FLAVOR_N, self.FLAVOR_OD),
        ];
        if upstream {
            t.push(("D".into(), 0.0, self.DRAIN_N, self.DRAIN_OD));
        }
        t
    }
    fn bores(&self, upstream: bool) -> Vec<(String, f64, f64, f64)> {
        let mut t: Vec<_> = self
            .tubes(upstream)
            .into_iter()
            .map(|(name, x, n, od)| (name, x, n, od - self.TUBE_DIAMETRIC_INTERFERENCE))
            .collect();
        t.extend(
            self.WIRE_X
                .iter()
                .enumerate()
                .map(|(i, x)| (format!("wire-{}", i + 1), *x, self.WIRE_N, self.WIRE_BORE)),
        );
        t
    }
    fn checks(&self) -> Result<Value> {
        let holes = self.bores(true);
        let mut pair_webs = Vec::new();
        for (i, (_, ax, an, ad)) in holes.iter().enumerate() {
            for (_, bx, bn, bd) in &holes[i + 1..] {
                pair_webs.push((ax - bx).hypot(an - bn) - (ad + bd) / 2.0);
            }
        }
        let minimum_web = pair_webs.into_iter().fold(f64::INFINITY, f64::min);
        let tube_reach = self
            .tubes(true)
            .iter()
            .map(|(_, x, n, od)| x.hypot(n - self.SHELL_CENTER_N) + od / 2.0)
            .fold(f64::NEG_INFINITY, f64::max);
        let wire_reach = self
            .WIRE_X
            .iter()
            .map(|x| x.hypot(self.WIRE_N - self.SHELL_CENTER_N) + 1.3 / 2.0)
            .fold(f64::NEG_INFINITY, f64::max);
        ensure!(
            tube_reach < self.STOP_ID / 2.0,
            "tube pack must clear gland stop"
        );
        ensure!(
            wire_reach < self.STOP_ID / 2.0,
            "wire pack must clear gland stop"
        );
        let face_web = minimum_web - 2.0 * self.BORE_LEAD_RADIAL;
        let width = 2.0 * (self.FLAVOR_X + self.FLAVOR_OD / 2.0);
        let shell_r = self.WATER_BEND_RADIUS + self.SHELL_CENTER_N;
        let floor_r = shell_r - crate::CAVITY_RADIUS;
        let keeper_clearance = (shell_r - self.TOOL_OD / 2.0)
            - (shell_r - self.KEEPER_ID / 2.0).hypot(self.BODY_MID_Z - self.KEEPER_LEAD_LENGTH);
        let offset = self.BODY_MID_Z * self.WATER_BEND_RADIUS / shell_r;
        let mut deviation = serde_json::Map::new();
        for (name, n) in [
            ("S", 0.0),
            ("F", self.FLAVOR_N),
            ("D", self.DRAIN_N),
            ("wire", self.WIRE_N),
        ] {
            deviation.insert(
                name.into(),
                json!(
                    self.WATER_BEND_RADIUS + n
                        - ((self.WATER_BEND_RADIUS + n).powi(2) - (self.BODY_LENGTH / 2.0).powi(2))
                            .sqrt()
                ),
            );
        }
        let far_z = self.BODY_MID_Z - self.KEEPER_LENGTH;
        let crown = shell_r + self.NECK_OD / 2.0 - (shell_r + self.GROOVE_ID / 2.0).hypot(far_z);
        let pi = std::f64::consts::PI;
        let gland = pi / 4.0
            * (self.KEEPER_ID.powi(2) * self.KEEPER_LENGTH
                + self.GROOVE_ID.powi(2) * self.GROOVE_LENGTH
                + self.BODY_SEAT_ID.powi(2) * self.BODY_LENGTH
                + self.UPSTREAM_STOP_ID.powi(2) * self.STOP_LENGTH);
        let occupied = pi / 4.0
            * (self.SODA_OD.powi(2)
                + 2.0 * self.FLAVOR_OD.powi(2)
                + self.DRAIN_OD.powi(2)
                + 4.0 * 1.3_f64.powi(2));
        let displacement = gland - occupied * self.GLAND_LENGTH;
        let mut free = pi / 4.0
            * (self.FLANGE_OD.powi(2) * self.FLANGE_LENGTH
                + self.BODY_OD.powi(2) * self.BODY_LENGTH);
        for (_, _, _, d) in holes {
            free -= pi / 4.0 * d * d * self.BUNG_LENGTH;
            free -= 2.0
                * pi
                * self.BORE_LEAD_DEPTH
                * (d / 2.0 * self.BORE_LEAD_RADIAL + self.BORE_LEAD_RADIAL.powi(2) / 3.0);
        }
        let body_space = pi / 4.0
            * (self.GROOVE_ID.powi(2) * self.GROOVE_LENGTH
                + self.BODY_SEAT_ID.powi(2) * self.BODY_LENGTH)
            - occupied * (self.GROOVE_LENGTH + self.BODY_LENGTH);
        let max_dev = ["S", "F", "D"]
            .iter()
            .map(|name| deviation[*name].as_f64().unwrap())
            .fold(f64::NEG_INFINITY, f64::max);
        Ok(
            json!({"minimum_uninstalled_web_mm":minimum_web,"minimum_web_at_bore_leads_mm":face_web,"minimum_nominal_installed_tube_web_mm":self.SEAL_WEB,"nominal_tube_web_compression_fraction":self.TUBE_DIAMETRIC_INTERFERENCE/(self.SEAL_WEB+self.TUBE_DIAMETRIC_INTERFERENCE),"tube_reach_from_shell_center_mm":tube_reach,"wire_reach_at_maximum_stated_envelope_mm":wire_reach,"stop_to_nominal_tube_clearance_mm":self.STOP_ID/2.0-tube_reach,"body_radial_interference_mm":(self.BODY_OD-self.BODY_SEAT_ID)/2.0,"flange_radial_interference_mm":(self.FLANGE_OD-self.GROOVE_ID)/2.0,"rigid_pusher_to_keeper_radial_clearance_mm":(self.KEEPER_ID-self.TOOL_OD)/2.0,"minimum_pusher_keeper_edge_clearance_over_rotation_mm":keeper_clearance,"pusher_inner_to_nominal_tube_clearance_mm":self.TOOL_ID/2.0-tube_reach,"pusher_slot_to_nominal_bundle_width_clearance_mm":self.TOOL_SLOT_WIDTH-width,"planar_groove_wall_mm":(self.NECK_OD-self.GROOVE_ID)/2.0,"free_bung_gland_body_axial_fit_mm":self.BODY_LENGTH,"flange_groove_axial_float_mm":self.GROOVE_LENGTH-self.FLANGE_LENGTH,"upstream_flange_capture_radial_overlap_mm":(self.GROOVE_ID-self.KEEPER_ID.max(self.BODY_SEAT_ID))/2.0,
   "planar_gland_alignment":{"local_z_at_body_midpoint_mm":self.BODY_MID_Z,"body_midpoint_arc_station_offset_mm":offset,"rule":"Align local Z=4.1 to the station at nominal_gland_s+offset; set local origin4.1 mm backward along its tangent. Clip the round cavity with actual planar mouth/stop faces.","maximum_tube_centre_deviation_in_body_mm":deviation,"minimum_nominal_tube_radial_interference_after_curvature_mm":self.TUBE_DIAMETRIC_INTERFERENCE/2.0-max_dev,"analytical_minimum_groove_crown_wall_mm":crown,"upstream_backstop_plane_floor_station_mm":crate::UPSTREAM_GLAND_S+offset+self.WATER_BEND_RADIUS*((self.GLAND_LENGTH-self.BODY_MID_Z)/floor_r).asin(),"downstream_keeper_plane_floor_station_mm":crate::DOWNSTREAM_GLAND_S+offset+self.WATER_BEND_RADIUS*(-self.BODY_MID_Z/floor_r).asin()},
   "elastomer_displacement_budget":{"method":"Straight maximum-wire-envelope volume budget; conservative because it excludes the extra keeper lead-in volume. Actual curved tubes and deformation are separate checks.","free_upstream_bung_volume_mm3":free,"body_and_groove_available_after_tubes_mm3":body_space,"minimum_axial_bulge_volume_mm3":(free-body_space).max(0.0),"keeper_and_backstop_opening_displacement_space_mm3":displacement-body_space,"complete_gland_available_after_tubes_mm3":displacement,"complete_gland_nominal_fill_fraction":free/displacement,"rule":"Leave keeper/backstop openings clear for axial rubber bulging. No solid clamp plate across the bung faces."},"scope":"Nominal free CAD dimensions. Elastomer deformation, as-printed bore size, cable jackets, tube extrusion variation, shell curved-wall reserve, assembly load, water containment and aging need separate readings.","passed":true}),
        )
    }
}
pub fn dispatch(r: &Value) -> Result<Value> {
    let d = Dimensions::new();
    let upstream = r["upstream"].as_bool().unwrap_or(true);
    Ok(match r["fn"].as_str().unwrap_or("datums") {
        "datums" => serde_json::to_value(d)?,
        "tube_centres" => json!(d.tubes(upstream)),
        "bore_centres" => json!(d.bores(upstream)),
        "check_geometry" => d.checks()?,
        x => bail!("unknown vent scalar operation {x}"),
    })
}
