//! The swept structural exterior every quadrant is trimmed to: the front round, the display
//! plane and the round onto the roof, and the print-down fills along the display's side edges.
use crate::catalog::outward_per_height;
use crate::{Bounds, P2};
pub use hsm_enclosure_interface::swept::{
    ANGLE, FLAT, FRONT_RADIUS, Profile, SIDE_RADIUS, TOP_RADIUS, profile,
};
use serde::{Deserialize, Serialize};

/// One section of the side-edge fill at the curved display top.
#[derive(Clone, Copy, Debug, Serialize, Deserialize)]
pub struct FillSection {
    pub x: f64,
    pub centre: P2,
    pub ellipse: [f64; 3],
    pub inner_radius: f64,
    pub start: P2,
    pub top_tangent: P2,
    pub inner_end: P2,
    pub inner_mid: P2,
    pub inner_start: P2,
    pub upper_roof: P2,
    pub lower_roof: P2,
    pub upper_aft: P2,
    pub lower_aft: P2,
}

/// The structure numbers every quadrant's evaluator reads beside its graph.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Structure {
    pub outer: Bounds,
    pub profile: Profile,
    pub standing_radius: f64,
    pub side_radius: f64,
    pub angle: f64,
    pub roof_fill_sections: [Vec<FillSection>; 2],
    pub roof_transition: RoofTransition,
}

#[derive(Clone, Copy, Debug, Serialize, Deserialize)]
pub struct RoofTransition {
    pub height: f64,
    pub foot: f64,
    pub outward_per_height: f64,
}

/// The funnel seat's thickness under the brim.
pub const FUNNEL_SEAT: f64 = 6.0;

/// The additive chamfer a print-down round takes: its height and its foot's reach.
pub fn transition(radius: f64) -> (f64, f64) {
    let slope = outward_per_height();
    let height = radius - radius * slope / (1.0 + slope * slope).sqrt();
    let inset = radius - radius / (1.0 + slope * slope).sqrt();
    (height, inset + slope * height)
}

/// The display keeps its side round; each section's ellipse joins that round to the roof's
/// print-down chamfer and overlaps the retained round, west edge then east.
pub fn roof_fill_sections(outer: &Bounds) -> [Vec<FillSection>; 2] {
    let p = profile(outer);
    let (radius, rt) = (SIDE_RADIUS, TOP_RADIUS);
    let angle = ANGLE.to_radians();
    let (sa, ca) = (angle.sin(), angle.cos());
    let (cy, cz) = (p.roof[0], outer[5] - rt);
    let aft = cy + 2.0 * radius;
    let (height, foot) = transition(radius);
    let tangent_depth = foot - outward_per_height() * height;
    let mut depths: Vec<f64> = (0..=90)
        .step_by(2)
        .map(|a| radius * (1.0 - (a as f64).to_radians().sin()))
        .filter(|&d| d >= tangent_depth)
        .chain([tangent_depth, foot, radius])
        .collect();
    depths.sort_by(f64::total_cmp);
    depths.dedup();
    [(outer[0], 1.0), (outer[1], -1.0)].map(|(edge, inward)| {
        depths
            .iter()
            .map(|&depth| {
                let side = radius - (radius * radius - (radius - depth) * (radius - depth)).max(0.0).sqrt();
                let roof = side.min(((foot - depth) / outward_per_height()).max(0.0));
                let side = side + 0.01;
                let (k, b) = (rt - side, rt - roof);
                let a = ((k * k - b * b * ca * ca) / (sa * sa)).sqrt();
                let inner_r = rt - side - 0.25;
                let inner_end = [cy - inner_r * sa, cz + inner_r * ca];
                FillSection {
                    x: edge + inward * depth,
                    centre: [cy, cz],
                    ellipse: [b, a, (a * sa).atan2(b * ca).to_degrees()],
                    inner_radius: inner_r,
                    start: [p.end[0] + sa * side - ca, p.end[1] - ca * side - sa],
                    top_tangent: [cy - a * a * sa / k, cz + b * b * ca / k],
                    inner_end,
                    inner_mid: [cy - inner_r * (angle / 2.0).sin(), cz + inner_r * (angle / 2.0).cos()],
                    inner_start: [inner_end[0] - ca, inner_end[1] - sa],
                    upper_roof: [cy, cz + b],
                    lower_roof: [cy, cz + inner_r],
                    upper_aft: [aft, cz + b],
                    lower_aft: [aft, cz + inner_r],
                }
            })
            .collect()
    })
}

pub fn structure(outer: &Bounds) -> Structure {
    let (height, foot) = transition(SIDE_RADIUS);
    Structure {
        outer: *outer,
        profile: profile(outer),
        standing_radius: FRONT_RADIUS,
        side_radius: SIDE_RADIUS,
        angle: ANGLE,
        roof_fill_sections: roof_fill_sections(outer),
        roof_transition: RoofTransition { height, foot, outward_per_height: outward_per_height() },
    }
}
