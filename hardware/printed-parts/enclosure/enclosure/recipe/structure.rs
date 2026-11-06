//! The swept structural exterior every quadrant is trimmed to: the front round, the display
//! plane and the round onto the roof, and the print-down fills along the display's side edges.
use crate::catalog::outward_per_height;
use crate::plan::Bounds;
use crate::shell::SHOW_EDGE_R;
pub use hsm_enclosure_solid::numbers::{FillSection, Profile, RoofTransition, Structure};

/// The display plane's tilt from level.
pub const ANGLE: f64 = 30.0;
/// The display plane's flat run.
pub const FLAT: f64 = 87.0;
pub const FRONT_RADIUS: f64 = 2.0 * SHOW_EDGE_R;
pub const TOP_RADIUS: f64 = 3.0 * SHOW_EDGE_R;
pub const SIDE_RADIUS: f64 = SHOW_EDGE_R;
/// The funnel seat's thickness under the brim.
pub const FUNNEL_SEAT: f64 = 6.0;

pub fn profile(outer: &Bounds) -> Profile {
    let (yf, zt) = (outer[2], outer[5]);
    let a = ANGLE.to_radians();
    let (rb, rt) = (FRONT_RADIUS, TOP_RADIUS);
    let zb = zt - rb * a.cos() - FLAT * a.sin() - rt * (1.0 - a.cos());
    let start = [yf + rb * (1.0 - a.sin()), zb + rb * a.cos()];
    let end = [start[0] + FLAT * a.cos(), start[1] + FLAT * a.sin()];
    let roof = [end[0] + rt * a.sin(), zt];
    let amid = (180.0 - (90.0 - ANGLE) / 2.0).to_radians();
    Profile {
        foot: [yf, zb],
        front_mid: [yf + rb + rb * amid.cos(), zb + rb * amid.sin()],
        start,
        end,
        top_mid: [roof[0] - rt * (a / 2.0).sin(), zt - rt + rt * (a / 2.0).cos()],
        roof,
        origin: [0.0, (start[0] + end[0]) / 2.0, (start[1] + end[1]) / 2.0],
        normal: [0.0, -a.sin(), a.cos()],
    }
}

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
