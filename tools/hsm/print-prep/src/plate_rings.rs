//! Writes the removable screw-seat rings under the Sculpted faucet's mounting plate.
//!
//! Each course joins an inner and an outer arc around each seat, with a single opening toward
//! the bed face, as the custom G-code the plate sequencer places among the mounting plate's
//! courses.

use crate::python_text::{dist, g, round};
use std::f64::consts::PI;
use std::fmt::Write;
use std::hint::black_box;

const CENTERS: [[f64; 2]; 3] = [[183., 106.], [205.5, 85.7], [228., 106.]];
const FIRST_Z: f64 = 0.20;
const PITCH: f64 = 0.24;
const COURSES: usize = 13;
const OPENING_ANGLE_DEGREES: f64 = 40.;
const ARC_SEGMENTS: usize = 32;
const TURN_SEGMENTS: usize = 6;
const TRAVEL_Z: f64 = 5.;
const FILAMENT_DIAMETER: f64 = 1.75;
const FLOW_RATIO: f64 = 0.9555;
const RETRACT: f64 = 0.8;

/// The cosine and sine from the platform's maths library, as the trial's Python takes them.
fn unit(angle: f64) -> [f64; 2] {
    let angle = black_box(angle);
    [angle.cos(), angle.sin()]
}

fn at(origin: [f64; 2], radial: [f64; 2], tangent: [f64; 2], r: f64, t: f64) -> [f64; 2] {
    [0, 1].map(|axis| round(origin[axis] + r * radial[axis] + t * tangent[axis], 5))
}

/// The inner arc, a half turn across the opening, and the outer arc back.
fn ring_path(center: [f64; 2], inner: f64, outer: f64) -> Vec<[f64; 2]> {
    let opening_angle = OPENING_ANGLE_DEGREES * (PI / 180.0);
    let start = -PI / 2.0 + opening_angle / 2.0;
    let span = 2.0 * PI - opening_angle;
    let angles: Vec<f64> = (0..=ARC_SEGMENTS).map(|i| start + span * i as f64 / ARC_SEGMENTS as f64).collect();
    let mut points: Vec<[f64; 2]> = angles.iter().map(|&a| at(center, unit(a), [0., 0.], inner, 0.)).collect();
    let radial = unit(angles[ARC_SEGMENTS]);
    let tangent = [-radial[1], radial[0]];
    let radius = (outer - inner) / 2.0;
    let middle = (outer + inner) / 2.0;
    for number in 1..=TURN_SEGMENTS {
        let [c, s] = unit(PI * number as f64 / TURN_SEGMENTS as f64);
        points.push(at(center, radial, tangent, middle - radius * c, radius * s));
    }
    points.extend(angles[..ARC_SEGMENTS].iter().rev().map(|&a| at(center, unit(a), [0., 0.], outer, 0.)));
    points
}

fn point(xy: [f64; 2]) -> String {
    format!("X{:.5} Y{:.5}", xy[0], xy[1])
}

/// The rings' G-code.
pub fn gcode() -> String {
    let mut out = String::new();
    for course in 0..COURSES {
        let z = round(FIRST_Z + course as f64 * PITCH, 2);
        let (height, width) = if course > 0 { (PITCH, 0.48) } else { (FIRST_Z, 0.55) };
        let (inner, outer) = if course > 0 { (2.06, 2.49) } else { (2.03, 2.53) };
        // The area matches the rounded-road convention of the donor.
        let e_per_mm = height * (width - height * (1.0 - PI / 4.0)) * FLOW_RATIO / (PI * (FILAMENT_DIAMETER / 2.0).powf(2.0));
        let rings: Vec<Vec<[f64; 2]>> = CENTERS.iter().map(|&center| ring_path(center, inner, outer)).collect();
        let (travel_feed, deposition_feed) = (9000, if course > 0 { 1800 } else { 1500 });
        let first = rings[0][0];
        let _ = writeln!(out, "; HSM_PLATE_RING_Z: {z:.2}");
        let _ = writeln!(out, "; HSM_ENTRY_XYZ: {:.5} {:.5} {z:.5}", first[0], first[1]);
        let _ = writeln!(out, "; HSM_ENTRY_RETRACT_MM: {}", g(RETRACT));
        out.push_str("M106 S0\nM204 S500\n");
        out.push_str(if course >= COURSES - 3 { "; FEATURE: Support interface\n" } else { "; FEATURE: Support\n" });
        let _ = writeln!(out, "; LINE_WIDTH: {}", g(width));
        let _ = writeln!(out, "; LAYER_HEIGHT: {}", g(height));
        for (index, path) in rings.iter().enumerate() {
            if index > 0 {
                let _ = writeln!(out, "G1 Z{TRAVEL_Z:.3} F900");
                let _ = writeln!(out, "G1 {} F{travel_feed}", point(path[0]));
                let _ = writeln!(out, "G1 Z{z:.5} F900");
            }
            let _ = writeln!(out, "G1 E{} F1800", g(RETRACT));
            let _ = writeln!(out, "G1 F{deposition_feed}");
            for pair in path.windows(2) {
                let amount = round(dist(&pair[0], &pair[1]) * e_per_mm, 6);
                let _ = writeln!(out, "G1 {} E{amount:.6}", point(pair[1]));
            }
            let _ = writeln!(out, "G1 E-{} F1800", g(RETRACT));
        }
    }
    out
}
