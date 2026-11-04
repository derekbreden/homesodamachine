//! Faucet scalar dimensions and numeric centreline recipes, in millimetres.
//!
//! X is lateral, Y is depth, and Z is up. The arc station is measured on
//! the water centreline after the internal 70-degree joint datum.

#![recursion_limit = "1024"]

use anyhow::{Context, Result, bail};
use serde_json::{Value, json};
pub mod assembly;
pub mod assembly_dimensions;
pub mod collar;
pub mod counter_plate;
pub mod covers;
pub mod geos;
pub mod lever;
pub mod plumbing;
pub mod shell;
pub mod shell_dimensions;
pub mod vent;

fn formatted(rows: &[(&str, f64, &str, &str)]) -> Value {
    let values: serde_json::Map<_, _> = rows
        .iter()
        .map(|(name, value, spec, suffix)| {
            (
                name.to_string(),
                Value::String(format!(
                    "{}{}",
                    hsm_documents::format_number(*value, spec).expect("literal number format"),
                    suffix
                )),
            )
        })
        .collect();
    Value::Object(values)
}

pub const WATER_Y: f64 = 8.875;
pub const WATER_OD: f64 = 9.525;
pub const FLAVOR_OD: f64 = 4.0;
pub const FLAVOR_ID: f64 = 2.5;
pub const FLAVOR_MIN_BEND: f64 = 25.0;
pub const DRAIN_OD: f64 = 4.0;
pub const DRAIN_ID: f64 = 2.5;
pub const LOWER_FLAVOR_X: f64 = 5.45;
pub const LOWER_BUNDLE_X: f64 = 0.0;
pub const LOWER_Y: f64 = 18.925;
pub const LOWER_DRAIN_Y: f64 = 18.525;
pub const LOWER_RIBBON_Y: f64 = 21.4875;
// Caliper observation: reference/bntechgo-signal-ribbon/physical-observations.json.
pub const RIBBON_WIDTH: f64 = 4.6;
pub const RIBBON_DEPTH: f64 = 1.18;
pub const LOWER_START_Z: f64 = 40.0;
pub const LOWER_END_Z: f64 = 67.5;
pub const LOWER_FLAVOR_FLARE: f64 = 0.10;
pub const OUTLET_Y: f64 = -133.99672200476698;
pub const OUTLET_Z: f64 = 180.38874339162197;
pub const TOTAL_ANGLE: f64 = 140.0 * std::f64::consts::PI / 180.0;
pub const TIP_LENGTH: f64 = 25.0;
pub const JOINT_ANGLE: f64 = 70.0 * std::f64::consts::PI / 180.0;
pub const SHELL_CENTER_N: f64 = 4.027512922;
pub const SHELL_RADIUS: f64 = 13.5;
pub const CAVITY_RADIUS: f64 = 11.5;
pub const SEAL_WEB: f64 = 0.8;
pub const TIGHT_RIBBON_N: f64 = 9.75;
pub const SEAL_RIBBON_N: f64 = 11.0125;
pub const FACE_RIBBON_N: f64 = 11.55;
pub const SPREAD_END_S: f64 = 14.0;
pub const UPSTREAM_GLAND_S: f64 = 30.0;
pub const DOWNSTREAM_GLAND_S: f64 = 59.3;
pub const GLAND_LENGTH: f64 = 7.3;
pub const GLAND_BODY_MID_Z: f64 = 4.1;
pub const DRAIN_END_ANGLE: f64 = 80.68709001137978 * std::f64::consts::PI / 180.0;
pub const CONVERGE_LENGTH: f64 = 24.0;
pub const RIBBON_CONVERGE_LENGTH: f64 = 8.0;
pub const PORT_LENGTH_S: f64 = 22.0;
pub const PORT_WIDTH: f64 = 12.0;
pub const PORT_CORNER_R: f64 = 2.0;
pub const DRIP_POCKET_ENTRY_S: f64 = 30.0;
pub const DRIP_POCKET_EXIT_S: f64 = 59.3;
pub const DRIP_GUIDE_WALL_THICKNESS: f64 = 2.0;
pub const DRIP_HOLE_DIAMETER: f64 = 4.0;
pub const DRIP_HOLE_ANGLE: f64 = 75.72139663878282 * std::f64::consts::PI / 180.0;
pub const DRIP_END_CLEARANCE_MM: f64 = 3.0;

pub fn water_radius() -> f64 {
    (WATER_Y - OUTLET_Y - TIP_LENGTH * TOTAL_ANGLE.sin()) / (1.0 - TOTAL_ANGLE.cos())
}
pub fn arc_start_z() -> f64 {
    OUTLET_Z - water_radius() * TOTAL_ANGLE.sin() - TIP_LENGTH * TOTAL_ANGLE.cos()
}
fn rf() -> f64 {
    (WATER_OD + FLAVOR_OD) / 2.0
}
fn rd() -> f64 {
    (DRAIN_OD + FLAVOR_OD) / 2.0
}
pub fn tight_drain_n() -> f64 {
    (WATER_OD + DRAIN_OD) / 2.0
}
pub fn tight_flavor_n() -> f64 {
    (rf().powi(2) - rd().powi(2) + tight_drain_n().powi(2)) / (2.0 * tight_drain_n())
}
pub fn tight_flavor_x() -> f64 {
    (rf().powi(2) - tight_flavor_n().powi(2)).sqrt()
}
pub fn face_flavor_x() -> f64 {
    FLAVOR_OD / 2.0
}
pub fn face_flavor_n() -> f64 {
    (rf().powi(2) - face_flavor_x().powi(2)).sqrt()
}
pub fn seal_drain_n() -> f64 {
    tight_drain_n() + SEAL_WEB
}
pub fn seal_flavor_n() -> f64 {
    ((rf() + SEAL_WEB).powi(2) - (rd() + SEAL_WEB).powi(2) + seal_drain_n().powi(2))
        / (2.0 * seal_drain_n())
}
pub fn seal_flavor_x() -> f64 {
    ((rf() + SEAL_WEB).powi(2) - seal_flavor_n().powi(2)).sqrt()
}
pub fn gland_mid_shift_s() -> f64 {
    GLAND_BODY_MID_Z * water_radius() / (water_radius() + SHELL_CENTER_N)
}
fn floor_radius() -> f64 {
    water_radius() + SHELL_CENTER_N - CAVITY_RADIUS
}
pub fn wet_start_s() -> f64 {
    UPSTREAM_GLAND_S
        + gland_mid_shift_s()
        + water_radius() * ((GLAND_LENGTH - GLAND_BODY_MID_Z) / floor_radius()).asin()
}
pub fn wet_end_s() -> f64 {
    DOWNSTREAM_GLAND_S
        + gland_mid_shift_s()
        + water_radius() * (-GLAND_BODY_MID_Z / floor_radius()).asin()
}
pub fn drain_cut_s() -> f64 {
    (DRAIN_END_ANGLE - JOINT_ANGLE) * water_radius()
}
pub fn converge_start_s() -> f64 {
    drain_cut_s() + 3.0
}
pub fn drip_floor_entry_s() -> f64 {
    DRIP_POCKET_ENTRY_S + water_radius() * (DRIP_GUIDE_WALL_THICKNESS / floor_radius()).asin()
}
pub fn drip_hole_s() -> f64 {
    (DRIP_HOLE_ANGLE - JOINT_ANGLE) * water_radius()
}

pub fn constants() -> Value {
    json!({
        "WATER_Y": WATER_Y, "WATER_OD": WATER_OD, "FLAVOR_OD": FLAVOR_OD,
        "FLAVOR_ID": FLAVOR_ID, "FLAVOR_MIN_BEND": FLAVOR_MIN_BEND,
        "DRAIN_OD": DRAIN_OD, "DRAIN_ID": DRAIN_ID,
        "LOWER_FLAVOR_X": LOWER_FLAVOR_X, "LOWER_BUNDLE_X": LOWER_BUNDLE_X,
        "LOWER_Y": LOWER_Y, "LOWER_DRAIN_Y": LOWER_DRAIN_Y, "LOWER_RIBBON_Y": LOWER_RIBBON_Y,
        "RIBBON_WIDTH": RIBBON_WIDTH, "RIBBON_DEPTH": RIBBON_DEPTH,
        "LOWER_START_Z": LOWER_START_Z, "LOWER_END_Z": LOWER_END_Z,
        "LOWER_FLAVOR_FLARE": LOWER_FLAVOR_FLARE,
        "OUTLET_Y": OUTLET_Y, "OUTLET_Z": OUTLET_Z, "TOTAL_ANGLE": TOTAL_ANGLE,
        "TIP_LENGTH": TIP_LENGTH, "WATER_RADIUS": water_radius(), "ARC_START_Z": arc_start_z(),
        "JOINT_ANGLE": JOINT_ANGLE, "SHELL_CENTER_N": SHELL_CENTER_N,
        "SHELL_RADIUS": SHELL_RADIUS, "CAVITY_RADIUS": CAVITY_RADIUS,
        "TIGHT_DRAIN_N": tight_drain_n(), "_rf": rf(), "_rd": rd(),
        "TIGHT_FLAVOR_N": tight_flavor_n(), "TIGHT_FLAVOR_X": tight_flavor_x(),
        "FACE_FLAVOR_X": face_flavor_x(), "FACE_FLAVOR_N": face_flavor_n(),
        "SEAL_WEB": SEAL_WEB, "SEAL_DRAIN_N": seal_drain_n(),
        "_seal_rf": rf() + SEAL_WEB, "_seal_rd": rd() + SEAL_WEB,
        "SEAL_FLAVOR_N": seal_flavor_n(), "SEAL_FLAVOR_X": seal_flavor_x(),
        "TIGHT_RIBBON_N": TIGHT_RIBBON_N, "SEAL_RIBBON_N": SEAL_RIBBON_N,
        "FACE_RIBBON_N": FACE_RIBBON_N, "SPREAD_END_S": SPREAD_END_S,
        "UPSTREAM_GLAND_S": UPSTREAM_GLAND_S, "DOWNSTREAM_GLAND_S": DOWNSTREAM_GLAND_S,
        "GLAND_LENGTH": GLAND_LENGTH, "GLAND_BODY_MID_Z": GLAND_BODY_MID_Z,
        "GLAND_MID_SHIFT_S": gland_mid_shift_s(), "_floor_radius": floor_radius(),
        "WET_START_S": wet_start_s(), "WET_END_S": wet_end_s(),
        "DRAIN_END_ANGLE": DRAIN_END_ANGLE, "DRAIN_CUT_S": drain_cut_s(),
        "CONVERGE_START_S": converge_start_s(), "CONVERGE_LENGTH": CONVERGE_LENGTH,
        "RIBBON_CONVERGE_LENGTH": RIBBON_CONVERGE_LENGTH, "PORT_START_S": wet_start_s(),
        "PORT_LENGTH_S": PORT_LENGTH_S, "PORT_WIDTH": PORT_WIDTH,
        "PORT_CORNER_R": PORT_CORNER_R, "DRIP_POCKET_ENTRY_S": DRIP_POCKET_ENTRY_S,
        "DRIP_POCKET_EXIT_S": DRIP_POCKET_EXIT_S,
        "DRIP_GUIDE_WALL_THICKNESS": DRIP_GUIDE_WALL_THICKNESS,
        "DRIP_HOLE_DIAMETER": DRIP_HOLE_DIAMETER, "DRIP_FLOOR_ENTRY_S": drip_floor_entry_s(),
        "DRIP_HOLE_ANGLE": DRIP_HOLE_ANGLE, "DRIP_HOLE_S": drip_hole_s(),
        "DRIP_END_CLEARANCE_MM": DRIP_END_CLEARANCE_MM,
    })
}

pub fn interface(slip: f64) -> Value {
    let pill_length_x = 18.15;
    let left = LOWER_BUNDLE_X - pill_length_x / 2.0;
    let right = LOWER_BUNDLE_X + pill_length_x / 2.0;
    json!({
        "flavor_tube_od": FLAVOR_OD, "flavor_tube_x_offset": LOWER_FLAVOR_X,
        "bundle_mount_x": LOWER_BUNDLE_X, "dispense_flavor_x_offset": FLAVOR_OD / 2.0,
        "flavor_tube_hole_clearance": 0.9, "flavor_tube_hole_dia": FLAVOR_OD + 0.9,
        "pill_length_x": pill_length_x, "pill_width_y": 7.25,
        "drain_tube_od": 4.0, "drain_tube_id": 2.5, "drain_bend_min_radius": 25.0,
        "drain_tube_gap": 0.25, "drain_tube_x": LOWER_BUNDLE_X, "drain_tube_y": LOWER_DRAIN_Y,
        "drain_tube_hole_dia": 4.0 + 0.9, "bundle_slot_left_x": left,
        "bundle_slot_right_x": right, "bundle_slot_length_x": right - left,
        "bundle_slot_center_x": (right + left) / 2.0, "flavor_tube_depth": LOWER_Y,
        "shank_hole_diameter": 12.6,
        "above_counter_plate_thickness": 4.0, "above_counter_gasket_thickness": 2.0,
        "display_housing_width": 24.50, "display_housing_length": 44.50,
        "display_pcb_width": 23.95, "display_pcb_length": 43.95,
        "display_corner_r": 5.75,
        "display_pcb_corner_r": 5.75 - (24.50 - 23.95) / 2.0,
        "display_total_depth": 10.35, "display_housing_depth": 5.0,
        "display_pcb_bottom_from_front": 6.45,
        "display_pcb_bottom_z": 10.35 - 6.45, "display_pcb_top_z": 10.35 - 5.0,
        "display_cover_slip": slip, "display_cover_lap": 2.0, "display_cover_over_face": 0.10,
    })
}

pub fn ease(t: f64) -> f64 {
    let t = t.clamp(0.0, 1.0);
    t * t * t * (10.0 + t * (-15.0 + 6.0 * t))
}
pub fn lower_positions(z: f64) -> [f64; 3] {
    let u = ease((z - LOWER_START_Z) / (LOWER_END_Z - LOWER_START_Z));
    let flare = LOWER_FLAVOR_FLARE * 4.0 * u * (1.0 - u);
    [
        LOWER_FLAVOR_X + (tight_flavor_x() - LOWER_FLAVOR_X) * u + flare,
        LOWER_Y - WATER_Y + (tight_flavor_n() - (LOWER_Y - WATER_Y)) * u,
        LOWER_DRAIN_Y - WATER_Y + (tight_drain_n() - (LOWER_DRAIN_Y - WATER_Y)) * u,
    ]
}
pub fn lower_bundle_x(z: f64) -> f64 {
    LOWER_BUNDLE_X * (1.0 - ease((z - LOWER_START_Z) / (LOWER_END_Z - LOWER_START_Z)))
}
pub fn lower_ribbon_y(z: f64) -> f64 {
    let u = ease((z - LOWER_START_Z) / (LOWER_END_Z - LOWER_START_Z));
    LOWER_RIBBON_Y + (WATER_Y + TIGHT_RIBBON_N - LOWER_RIBBON_Y) * u
}
pub fn lower_point(z: f64, kind: &str, sign: f64) -> [f64; 3] {
    let [x, f, d] = lower_positions(z);
    let y = if kind == "ribbon" {
        lower_ribbon_y(z)
    } else {
        WATER_Y + if kind == "flavor" { f } else { d }
    };
    [
        lower_bundle_x(z) + if kind == "flavor" { sign * x } else { 0.0 },
        y,
        z,
    ]
}
pub fn positions(s: f64) -> [f64; 5] {
    let u = ease((s - converge_start_s()) / CONVERGE_LENGTH);
    let a0 = tight_flavor_x().atan2(tight_flavor_n());
    let a1 = face_flavor_x().atan2(face_flavor_n());
    let angle = a0 + (a1 - a0) * u;
    let cable_u = ease((s - converge_start_s()) / RIBBON_CONVERGE_LENGTH);
    [
        rf() * angle.sin(),
        rf() * angle.cos(),
        tight_drain_n(),
        TIGHT_RIBBON_N + (FACE_RIBBON_N - TIGHT_RIBBON_N) * cable_u,
        RIBBON_WIDTH,
    ]
}
pub fn arc_point(angle: f64, x: f64, n: f64) -> [f64; 3] {
    [
        x,
        WATER_Y - water_radius() + (water_radius() + n) * angle.cos(),
        arc_start_z() + (water_radius() + n) * angle.sin(),
    ]
}
pub fn station_point(s: f64, x: f64, n: f64) -> [f64; 3] {
    arc_point(JOINT_ANGLE + s / water_radius(), x, n)
}
pub fn station_plane(s: f64, center_n: f64) -> [[f64; 3]; 3] {
    let a = JOINT_ANGLE + s / water_radius();
    [
        station_point(s, 0.0, center_n),
        [1.0, 0.0, 0.0],
        [0.0, -a.sin(), a.cos()],
    ]
}
pub fn tube_arc_point(s: f64, kind: &str, sign: f64) -> [f64; 3] {
    let [x, f, d, ribbon, _] = positions(s);
    station_point(
        s,
        if kind == "flavor" { sign * x } else { 0.0 },
        if kind == "flavor" {
            f
        } else if kind == "drain" {
            d
        } else {
            ribbon
        },
    )
}
pub fn port_half_width(s: f64) -> f64 {
    let q = s - wet_start_s();
    if !(0.0..=PORT_LENGTH_S).contains(&q) {
        return 0.0;
    }
    let d = q.min(PORT_LENGTH_S - q);
    if d >= PORT_CORNER_R {
        PORT_WIDTH / 2.0
    } else {
        PORT_WIDTH / 2.0 - PORT_CORNER_R
            + (PORT_CORNER_R.powi(2) - (d - PORT_CORNER_R).powi(2))
                .max(0.0)
                .sqrt()
    }
}

fn line(legs: &mut Vec<Value>, a: [f64; 3], b: [f64; 3]) {
    // The threshold excludes only coincident endpoints.
    if (a[0] - b[0]).hypot(a[1] - b[1]).hypot(a[2] - b[2]) > 1e-7 {
        legs.push(json!(["line", a, b]));
    }
}
fn spline(legs: &mut Vec<Value>, point: impl Fn(f64) -> [f64; 3], a: f64, b: f64) {
    let count = (((b - a) / 0.4).ceil() as usize).max(16);
    let points: Vec<_> = (0..=count)
        .map(|i| point(a + (b - a) * i as f64 / count as f64))
        .collect();
    legs.push(json!(["spline", points]));
}
fn constant_arc(legs: &mut Vec<Value>, a: f64, b: f64, x: f64, n: f64) {
    if b - a > 1e-9 {
        legs.push(json!([
            "arc",
            arc_point(a, x, n),
            arc_point((a + b) / 2.0, x, n),
            arc_point(b, x, n)
        ]));
    }
}
pub fn path_legs(kind: &str, bottom_z: f64, sign: f64, end_s: Option<f64>) -> Vec<Value> {
    let mut legs = vec![];
    let lower = |z| lower_point(z, kind, sign);
    let start = lower(LOWER_START_Z);
    line(&mut legs, [start[0], start[1], bottom_z], start);
    spline(&mut legs, lower, LOWER_START_Z, LOWER_END_Z);
    let ty = lower(LOWER_END_Z)[1];
    let mut nx = if kind == "flavor" {
        sign * tight_flavor_x()
    } else {
        0.0
    };
    let mut nn = if kind == "flavor" {
        tight_flavor_n()
    } else if kind == "drain" {
        tight_drain_n()
    } else {
        TIGHT_RIBBON_N
    };
    line(&mut legs, lower(LOWER_END_Z), [nx, ty, arc_start_z()]);
    constant_arc(&mut legs, 0.0, JOINT_ANGLE, nx, nn);
    let end_s = if kind == "drain" {
        end_s.or_else(|| Some(drain_cut_s()))
    } else {
        end_s
    };
    if let Some(end) = end_s {
        if end <= converge_start_s() {
            constant_arc(
                &mut legs,
                JOINT_ANGLE,
                JOINT_ANGLE + end / water_radius(),
                nx,
                nn,
            );
        } else {
            constant_arc(
                &mut legs,
                JOINT_ANGLE,
                JOINT_ANGLE + converge_start_s() / water_radius(),
                nx,
                nn,
            );
            spline(
                &mut legs,
                |s| tube_arc_point(s, kind, sign),
                converge_start_s(),
                end,
            );
        }
    } else {
        constant_arc(
            &mut legs,
            JOINT_ANGLE,
            JOINT_ANGLE + converge_start_s() / water_radius(),
            nx,
            nn,
        );
        spline(
            &mut legs,
            |s| tube_arc_point(s, kind, sign),
            converge_start_s(),
            converge_start_s() + CONVERGE_LENGTH,
        );
        let p = positions(converge_start_s() + CONVERGE_LENGTH);
        (nx, nn) = if kind == "flavor" {
            (sign * p[0], p[1])
        } else {
            (0.0, p[3])
        };
        constant_arc(
            &mut legs,
            JOINT_ANGLE + (converge_start_s() + CONVERGE_LENGTH) / water_radius(),
            TOTAL_ANGLE,
            nx,
            nn,
        );
        let start = arc_point(TOTAL_ANGLE, nx, nn);
        line(
            &mut legs,
            start,
            [
                start[0],
                start[1] - TIP_LENGTH * TOTAL_ANGLE.sin(),
                start[2] + TIP_LENGTH * TOTAL_ANGLE.cos(),
            ],
        );
    }
    legs
}

/// TPU thimble dimensions, cap down. The cap bore continues into its open sleeve.
pub fn o_ring(color: &Value) -> Value {
    let inner_diameter = 9.2;
    let outer_diameter = 10.44;
    let cap_hole_diameter = 6.50;
    let cap_thickness = 2.1;
    let cylinder_length = 13.5;
    let total_height = cap_thickness + cylinder_length;
    let wall_thickness = (outer_diameter - inner_diameter) / 2.0;
    let lldpe_od = 9.525;
    let lldpe_id = 6.35;
    let westbrass_port_diameter = 10.0;
    let port_depth_min = 20.0;
    let westbrass_squeeze = (outer_diameter - westbrass_port_diameter) / 2.0;
    let lldpe_interference = (lldpe_od - inner_diameter) / 2.0;
    let variables = formatted(&[
        ("ORING_INNER_D", inner_diameter, ".4g", " mm"),
        ("ORING_OUTER_D", outer_diameter, ".4g", " mm"),
        ("CAP_HOLE_D", cap_hole_diameter, ".4g", " mm"),
        ("ORING_CAP_T", cap_thickness, ".4g", " mm"),
        ("CYL_L", cylinder_length, ".4g", " mm"),
        ("TOTAL_H", total_height, ".4g", " mm"),
        ("ORING_WALL_T", wall_thickness, ".4g", " mm"),
        ("LLDPE_OD", lldpe_od, ".4g", " mm"),
        ("LLDPE_ID", lldpe_id, ".4g", " mm"),
        ("WESTBRASS_PORT_D", westbrass_port_diameter, ".4g", " mm"),
        ("PORT_DEPTH_MIN", port_depth_min, ".4g", " mm"),
        ("WESTBRASS_SQUEEZE", westbrass_squeeze, ".4g", " mm"),
        ("LLDPE_INTERFERENCE", lldpe_interference, ".4g", " mm"),
    ]);
    json!({
        "variables": variables,
        "datums": {
            "inner_diameter": inner_diameter, "outer_diameter": outer_diameter,
            "cap_hole_diameter": cap_hole_diameter, "cap_thickness": cap_thickness,
            "cylinder_length": cylinder_length, "total_height": total_height,
            "wall_thickness": wall_thickness, "lldpe_od": lldpe_od, "lldpe_id": lldpe_id,
            "westbrass_port_diameter": westbrass_port_diameter, "port_depth_min": port_depth_min,
            "westbrass_squeeze": westbrass_squeeze, "lldpe_interference": lldpe_interference,
        },
        "numbers": {
            "name": "tpu-o-ring", "color": color,
            "outer_radius": outer_diameter / 2.0, "inner_radius": inner_diameter / 2.0,
            "cap_hole_radius": cap_hole_diameter / 2.0,
            "cap_thickness": cap_thickness, "total_height": total_height,
        },
    })
}

/// Round organizer stock, five passages and their axes in the faucet's mounting frame.
pub fn organizer(color: &Value) -> Value {
    let od = 32.0;
    let length = 10.0;
    let tube_bore = 6.65;
    let drain_bore = 4.40;
    let flavor_bore = drain_bore;
    let cable_slot_length = 5.4;
    let cable_slot_depth = 1.8;
    let min_material = 1.50;
    let entry = 0.40;
    let cable_entry = 0.20;
    let outside_ease = 0.20;
    let flavor_spread = 2.40;
    let flavor_forward = 1.80;
    let drain_forward = 2.30;
    let cable_xy = [LOWER_BUNDLE_X, LOWER_RIBBON_Y];
    let flavor_x = LOWER_FLAVOR_X + flavor_spread;
    let flavor_y = LOWER_Y - flavor_forward;
    let center_xy = [
        LOWER_BUNDLE_X,
        (flavor_x.powi(2) + flavor_y.powi(2) - LOWER_BUNDLE_X.powi(2)) / (2.0 * flavor_y),
    ];
    let bores = [
        ("S", [0.0, 0.0], tube_bore),
        (
            "F1",
            [LOWER_BUNDLE_X + LOWER_FLAVOR_X + flavor_spread, flavor_y],
            flavor_bore,
        ),
        (
            "F2",
            [LOWER_BUNDLE_X - LOWER_FLAVOR_X - flavor_spread, flavor_y],
            flavor_bore,
        ),
        (
            "D",
            [LOWER_BUNDLE_X, LOWER_DRAIN_Y - drain_forward],
            drain_bore,
        ),
        ("SIG", cable_xy, cable_slot_length),
    ];
    let datum_bores: Vec<_> = bores
        .iter()
        .map(|(name, xy, diameter)| json!([name, xy, diameter]))
        .collect();
    let number_bores: Vec<_> = bores
        .iter()
        .map(|(name, xy, diameter)| {
            json!({
                "name": name, "center": [xy[0] - center_xy[0], xy[1] - center_xy[1]],
                "radius": diameter / 2.0, "entry": if *name == "SIG" {cable_entry} else {entry},
            })
        })
        .collect();
    let mut variables = formatted(&[
        ("ORGANIZER_OD", od, "g", " mm"),
        ("ORGANIZER_LENGTH", length, "g", " mm"),
        ("ORGANIZER_TUBE_BORE", tube_bore, ".2f", " mm"),
        ("ORGANIZER_DRAIN_BORE", drain_bore, ".2f", " mm"),
        ("ORGANIZER_FLAVOR_BORE", flavor_bore, ".2f", " mm"),
        ("ORGANIZER_ENTRY", entry, "g", " mm"),
        ("ORGANIZER_CONTACT", length - 2.0 * entry, "g", " mm"),
        ("ORGANIZER_CABLE_ENTRY", cable_entry, "g", " mm"),
        ("ORGANIZER_RIM_EASE", outside_ease, "g", " mm"),
        ("ORGANIZER_MIN_MATERIAL", min_material, "g", " mm"),
        ("ORGANIZER_FLAVOR_SPREAD", flavor_spread, "g", " mm"),
        ("ORGANIZER_FLAVOR_FORWARD", flavor_forward, "g", " mm"),
        ("ORGANIZER_DRAIN_FORWARD", drain_forward, "g", " mm"),
    ]);
    variables["ORGANIZER_CABLE_SLOT"] = Value::String(format!(
        "{} × {} mm",
        hsm_documents::format_number(cable_slot_length, "g").expect("literal number format"),
        hsm_documents::format_number(cable_slot_depth, "g").expect("literal number format")
    ));
    json!({
        "variables": variables,
        "datums": {
            "OD": od, "LENGTH": length, "TUBE_BORE": tube_bore,
            "DRAIN_BORE": drain_bore, "FLAVOR_BORE": flavor_bore,
            "CABLE_SLOT_LENGTH": cable_slot_length, "CABLE_SLOT_DEPTH": cable_slot_depth,
            "MIN_MATERIAL": min_material, "ENTRY": entry, "CABLE_ENTRY": cable_entry,
            "OUTSIDE_EASE": outside_ease, "FLAVOR_SPREAD": flavor_spread,
            "FLAVOR_FORWARD": flavor_forward, "DRAIN_FORWARD": drain_forward,
            "CABLE_XY": cable_xy, "_flavor_x": flavor_x, "_flavor_y": flavor_y,
            "CENTRE_XY": center_xy, "BORES": datum_bores,
        },
        "numbers": {
            "name": "umbilical-organizer", "color": color,
            "stock_radius": od / 2.0, "length": length, "outside_ease": outside_ease,
            "bore_overrun": 1.0, "slot_length": cable_slot_length,
            "slot_depth": cable_slot_depth, "bores": number_bores,
        },
    })
}

/// Countertop stack recipes. The shell supplies its authored foot and screw-seat
/// measurements and lower passage sections; this program owns the stacking math.
pub fn countertop_stack(
    kind: &str,
    shell: &Value,
    lower_bundle: &Value,
    color: &Value,
) -> Result<Value> {
    let f = |key: &str| {
        shell[key]
            .as_f64()
            .with_context(|| format!("shell has no numeric {key}"))
    };
    let foot_width = f("foot_width")?;
    let foot_depth = f("foot_depth")?;
    let foot_center_y = f("foot_center_y")?;
    let plate_thickness = 4.0;
    let gasket_thickness = 2.0;
    let shank_hole_diameter = 12.6;
    let shank_hole_center = [0.0, 0.0];
    let flavor_center = [LOWER_BUNDLE_X, LOWER_Y];
    let mut numbers = json!({
        "name": kind, "color": color,
        "foot_width": foot_width, "foot_depth": foot_depth, "foot_center_y": foot_center_y,
        "shank_hole_center": shank_hole_center, "shank_hole_radius": shank_hole_diameter / 2.0,
        "pill_slot_center": flavor_center, "pill_length_x": 18.15, "pill_width_y": 7.25,
    });
    let (datums, variables) = if kind == "above-counter-plate" {
        let pedestal_dia = f("base_pedestal_dia")?;
        let pedestal_height = f("base_pedestal_height")?;
        let pedestal_chamfer = f("base_pedestal_chamfer")?;
        let pod_shank_dia = f("base_pod_shank_dia")?;
        let counterbore_dia = f("base_pod_counterbore_dia")?;
        let counterbore_depth = f("base_screw_counterbore_depth")?;
        let seat_thickness = f("base_plate_seat_thickness")?;
        let screw_length = f("base_screw_length")?;
        let signal_exit_x = f("signal_lower_exit_x")?;
        let signal_exit_y = f("signal_lower_exit_y")?;
        let z_range = [-plate_thickness, 0.0];
        numbers["plate_z"] = json!(z_range);
        for key in [
            "base_pod_centers",
            "base_pedestal_dia",
            "base_pedestal_height",
            "base_pedestal_chamfer",
            "base_pod_shank_dia",
            "base_pod_counterbore_dia",
            "base_screw_counterbore_depth",
        ] {
            numbers[key] = shell
                .get(key)
                .with_context(|| format!("shell has no {key}"))?
                .clone();
        }
        (
            json!({
                "plate_thickness": plate_thickness, "plate_z_range": z_range,
                "plate_center": [0.0,foot_center_y], "shank_diameter_nominal": 11.0,
                "shank_hole_radius": shank_hole_diameter/2.0,
                "shank_hole_center": shank_hole_center, "pill_slot_center": flavor_center,
            }),
            formatted(&[
                ("PLATE_T", plate_thickness, ".4g", " mm"),
                ("PLATE_Z_BOTTOM", z_range[0], ".4g", ""),
                ("PLATE_Y", foot_center_y, ".4g", " mm"),
                ("FOOT_WIDTH", foot_width, ".4g", " mm"),
                ("FOOT_DEPTH", foot_depth, ".4g", " mm"),
                ("PEDESTAL_CHAMFER", pedestal_chamfer, ".4g", " mm"),
                ("CBORE_D", counterbore_dia, ".4g", " mm"),
                ("CBORE_DEPTH", counterbore_depth, ".4g", " mm"),
                ("SEAT_T", seat_thickness, ".4g", " mm"),
                ("PEDESTAL_D", pedestal_dia, ".4g", " mm"),
                ("PEDESTAL_H", pedestal_height, ".4g", " mm"),
                ("SCREW_LENGTH", screw_length, ".4g", " mm"),
                ("SHANK_D", pod_shank_dia, ".4g", " mm"),
                ("SHANK_HOLE_D", shank_hole_diameter, ".4g", " mm"),
                ("PLATE_FLAVOR_Y", LOWER_Y, ".4g", " mm"),
                ("PLATE_FLAVOR_X", LOWER_BUNDLE_X, ".4g", " mm"),
                ("PLATE_RIBBON_X", signal_exit_x, ".4g", " mm"),
                ("PLATE_RIBBON_Y", signal_exit_y, ".6g", " mm"),
                ("PLATE_PILL_L", 18.15, ".4g", " mm"),
                ("PLATE_PILL_W", 7.25, ".4g", " mm"),
            ]),
        )
    } else if kind == "above-counter-gasket" {
        let plate_z_bottom = -plate_thickness;
        let z_range = [plate_z_bottom - gasket_thickness, plate_z_bottom];
        numbers["gasket_z"] = json!(z_range);
        (
            json!({
                "gasket_thickness": gasket_thickness, "gasket_center": [0.0,foot_center_y],
                "plate_z_bottom": plate_z_bottom, "gasket_z_range": z_range,
                "shank_hole_center": shank_hole_center, "flavor_tube_center": flavor_center,
            }),
            formatted(&[
                ("GASKET_T", gasket_thickness, ".4g", " mm"),
                ("GASKET_Y", foot_center_y, ".4g", " mm"),
                ("SHANK_HOLE_D", shank_hole_diameter, ".4g", " mm"),
                ("FLAVOR_TUBE_Y", LOWER_Y, ".4g", " mm"),
                ("PILL_L", 18.15, ".4g", " mm"),
                ("PILL_W", 7.25, ".4g", " mm"),
            ]),
        )
    } else {
        bail!("unknown countertop stack part {kind:?}");
    };
    let extra = lower_bundle
        .as_object()
        .context("lower bundle recipe must be an object")?;
    numbers
        .as_object_mut()
        .expect("recipe object")
        .extend(extra.clone());
    Ok(json!({"datums":datums,"numbers":numbers,"variables":variables}))
}

pub fn dispatch(request: &Value) -> Result<Value> {
    let op = request["op"].as_str().unwrap_or("");
    let args = request["args"].as_array().cloned().unwrap_or_default();
    let kwargs = &request["kwargs"];
    let f = |i: usize, default: f64| args.get(i).and_then(Value::as_f64).unwrap_or(default);
    let kind = |i: usize| args.get(i).and_then(Value::as_str).unwrap_or("flavor");
    Ok(match op {
        "constants" => constants(),
        "interface" => interface(f(0, 0.15)),
        "display-snap" => covers::snap(),
        "consumer-cover" => covers::consumer(request)?,
        "industrial-cover" => covers::industrial_cover(request)?,
        "industrial-body" => covers::industrial_body(request)?,
        "lever" => lever::data(&request["color"])?,
        "lever-repack" => lever::repack(request)?,
        "pchip" => lever::pchip_request(request)?,
        "under-counter-plate" => counter_plate::dispatch(request)?,
        "shell" => shell::dispatch(request)?,
        "collar" => collar::dispatch(request)?,
        "geos-library" => geos::info()?,
        "assembly" => assembly::dispatch(request)?,
        "vent" => vent::dispatch(request)?,
        "plumbing" => plumbing::dispatch(request)?,
        "o-ring" => o_ring(&request["color"]),
        "organizer" => organizer(&request["color"]),
        "above-counter-plate" | "above-counter-gasket" => countertop_stack(
            op,
            &request["shell"],
            &request["lower_bundle"],
            &request["color"],
        )?,
        "ease" => json!(ease(f(0, 0.0))),
        "lower_positions" => json!(lower_positions(f(0, 0.0))),
        "lower_bundle_x" => json!(lower_bundle_x(f(0, 0.0))),
        "lower_ribbon_y" => json!(lower_ribbon_y(f(0, 0.0))),
        "lower_point" => json!(lower_point(f(0, 0.0), kind(1), f(2, 1.0))),
        "positions" => json!(positions(f(0, 0.0))),
        "arc_point" => json!(arc_point(f(0, 0.0), f(1, 0.0), f(2, 0.0))),
        "station_point" => json!(station_point(f(0, 0.0), f(1, 0.0), f(2, 0.0))),
        "station_plane" => json!(station_plane(
            f(0, 0.0),
            kwargs["center_n"].as_f64().unwrap_or(0.0)
        )),
        "tube_arc_point" => json!(tube_arc_point(f(0, 0.0), kind(1), f(2, 1.0))),
        "port_half_width" => json!(port_half_width(f(0, 0.0))),
        "path_legs" => json!(path_legs(
            kind(0),
            f(1, -6.2),
            f(2, 1.0),
            kwargs["end_s"].as_f64()
        )),
        _ => bail!("unknown faucet-data operation {op:?}"),
    })
}
