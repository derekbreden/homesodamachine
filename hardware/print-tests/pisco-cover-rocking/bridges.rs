//! Short flat lands in the receiver and matching teeth on the cover resist withdrawal across both wings.
use super::stations::{REACH, catch_air, corbel_slope};
use anyhow::Result;
use hsm_enclosure_numbers::layout::{PISCO_WING_AFT_Y, Station};
use hsm_kernel::{Solid, v3};
use serde_json::{Value, json};

const FLAT_INSET: f64 = 0.65;
const FLAT_AIR: f64 = 0.10;
const END_AIR: f64 = 0.25;
const JOIN: f64 = 0.20;
const MODIFIER_X_MARGIN: f64 = 0.50;
const MODIFIER_END_LANDING: f64 = 1.20;
const MODIFIER_Z_MARGIN: f64 = 0.75;

/// Uncut receiver chamfers at both ends of every window support the bridge roads.
fn windows(st: &Station, long: bool) -> (Vec<[f64; 2]>, f64) {
    let (count, span) = if long { (2, 8.0) } else { (4, 4.0) };
    let landing = (PISCO_WING_AFT_Y - st.y0 - f64::from(count) * span) / f64::from(count + 1);
    let spans = (0..count).map(|i| {
        let fore = st.y0 + landing + f64::from(i) * (span + landing);
        [fore, fore + span]
    }).collect();
    (spans, landing)
}

struct Shoulder {
    edge_z: f64,
    receiver_z: f64,
    cover_z: f64,
    receiver_outer: f64,
    tooth_outer: f64,
    nose: f64,
    ramp_advance: f64,
}

impl Shoulder {
    fn at(st: &Station) -> Self {
        let slope = corbel_slope();
        let edge_z = st.bearing - REACH * slope;
        let receiver_z = edge_z + FLAT_INSET * slope;
        let receiver_outer = st.ledge - FLAT_INSET;
        Self {
            edge_z,
            receiver_z,
            cover_z: receiver_z + FLAT_AIR,
            receiver_outer,
            // Extend the tooth outward until its flat meets the original hook face continuously.
            tooth_outer: receiver_outer + (catch_air() - FLAT_AIR) / slope,
            nose: st.ledge - REACH,
            // In the cap's end-print pose the ramp advances normal to the existing hook outline.
            ramp_advance: 1.0_f64.hypot(slope),
        }
    }

    fn ramp_length(&self, radius: f64) -> f64 {
        (self.tooth_outer - radius) * corbel_slope() / self.ramp_advance
    }

    /// The cut stops at the existing neck and preserves its full height behind the hook nose.
    fn relief(&self, st: &Station, side: f64, [fore, aft]: [f64; 2]) -> Solid {
        let [x0, x1] = x_bounds(st, side, st.neck, self.receiver_outer);
        let top = self.edge_z + (st.ledge - st.neck) * corbel_slope() + JOIN;
        Solid::cuboid(v3(x0, fore, self.receiver_z), v3(x1, aft, top))
    }

    /// The fore ramp grows from the existing chamfer to the horizontal tooth. Its aft end faces up in the print.
    fn tooth(&self, st: &Station, side: f64, [fore, aft]: [f64; 2]) -> Result<Solid> {
        let (start, end) = (fore + END_AIR, aft - END_AIR);
        let mut corners = Vec::new();
        for radius in [self.nose, self.tooth_outer] {
            let x = st.axis_x + side * radius;
            let original_z = self.cover_z + (self.tooth_outer - radius) * corbel_slope();
            corners.extend([
                v3(x, start, original_z + JOIN),
                v3(x, start, original_z),
                v3(x, start + self.ramp_length(radius), self.cover_z),
                v3(x, end, self.cover_z),
                v3(x, end, original_z + JOIN),
            ]);
        }
        Solid::hull(&corners)
    }
}

fn x_bounds(st: &Station, side: f64, inner: f64, outer: f64) -> [f64; 2] {
    let a = st.axis_x + side * inner;
    let b = st.axis_x + side * outer;
    [a.min(b), a.max(b)]
}

pub fn receiver(base: &Solid, st: &Station, long: bool) -> Result<Solid> {
    let shoulder = Shoulder::at(st);
    let mut cuts = Vec::new();
    for span in windows(st, long).0 {
        for side in [-1.0, 1.0] {
            cuts.push(shoulder.relief(st, side, span));
        }
    }
    base.cut_all(&cuts)
}

pub fn cover(cap: &Solid, st: &Station, long: bool) -> Result<Solid> {
    let shoulder = Shoulder::at(st);
    let mut solids = vec![cap.clone()];
    for span in windows(st, long).0 {
        for side in [-1.0, 1.0] {
            solids.push(shoulder.tooth(st, side, span)?);
        }
    }
    Solid::union_all(&solids)
}

/// The slice review and mesh checks use the same window, landing and tooth limits that form the solids.
pub fn details(st: &Station, long: bool) -> Value {
    let shoulder = Shoulder::at(st);
    let (spans, landing) = windows(st, long);
    let span_length = spans[0][1] - spans[0][0];
    let tooth_length = span_length - 2.0 * END_AIR;
    let full_width_length = tooth_length - shoulder.ramp_length(shoulder.nose);
    let engaged_width = shoulder.receiver_outer - shoulder.nose;
    let middle_radius = (shoulder.nose + shoulder.receiver_outer) / 2.0;
    let bearing_area = engaged_width * (tooth_length - shoulder.ramp_length(middle_radius));
    let mut rows = Vec::new();
    let mut modifiers = Vec::new();
    for (i, &[fore, aft]) in spans.iter().enumerate() {
        for (side, label) in [(-1.0, "west"), (1.0, "east")] {
            let [x0, x1] = x_bounds(st, side, st.neck, shoulder.receiver_outer);
            let bounds = [x0 - MODIFIER_X_MARGIN, x1 + MODIFIER_X_MARGIN, fore - MODIFIER_END_LANDING,
                          aft + MODIFIER_END_LANDING, shoulder.receiver_z - MODIFIER_Z_MARGIN,
                          shoulder.receiver_z + MODIFIER_Z_MARGIN];
            let start = fore + END_AIR;
            let end = aft - END_AIR;
            rows.push(json!({
                "side": label, "window_index": i + 1, "window_y_mm": [fore, aft],
                "tooth_y_mm": [start, end],
                "full_width_tooth_y_mm": [start + shoulder.ramp_length(shoulder.nose), end],
                "receiver_flat_x_mm": [x0, x1],
                "tooth_flat_x_mm": x_bounds(st, side, shoulder.nose, shoulder.tooth_outer),
                "engaged_flat_x_mm": x_bounds(st, side, shoulder.nose, shoulder.receiver_outer),
                "receiver_flat_z_mm": shoulder.receiver_z, "tooth_flat_z_mm": shoulder.cover_z,
                "bridge_override_bounds_mm": bounds,
            }));
            modifiers.push(json!({
                "name": format!("Pisco {label} shoulder {}", i + 1), "bounds_source_mm": bounds,
                "bridge_axis_source": [0, 1, 0], "bridge_print_axis_source": [0, 1, 0],
                "bridge_span_mm": span_length, "reason": "The bridge roads land on the uncut chamfer at each end of the window."
            }));
        }
    }
    json!({
        "bounds_order": ["xmin", "xmax", "ymin", "ymax", "zmin", "zmax"],
        "wing_y_mm": [st.y0, PISCO_WING_AFT_Y], "uncut_landing_y_mm": landing,
        "ledge_edge_z_mm": shoulder.edge_z, "flat_inset_from_ledge_edge_mm": FLAT_INSET,
        "shoulder_tooth_nominal_gap_z_mm": FLAT_AIR, "original_chamfer_gap_z_mm": catch_air(),
        "nose_capture_x_mm": REACH, "nose_to_neck_x_mm": shoulder.nose - st.neck,
        "tooth_end_air_y_mm": END_AIR, "engaged_flat_width_x_mm": engaged_width,
        "fore_ramp_angle_to_print_bed_deg": 45.0,
        "fore_ramp_run_at_nose_y_mm": shoulder.ramp_length(shoulder.nose),
        "full_width_bearing_length_per_tooth_mm": full_width_length,
        "full_width_bearing_length_per_side_mm": full_width_length * spans.len() as f64,
        "projected_flat_bearing_area_per_side_mm2": bearing_area * spans.len() as f64,
        "windows": rows, "bridge_regions": modifiers,
    })
}
