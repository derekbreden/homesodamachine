//! The cold core's bore corridors as the lines and circular arcs its internal routes fit them
//! with, from the cold core's own corner fitting.
use super::wire_request::Segment;
use anyhow::Result;
use hsm_kernel::math::{acos, sin, tan};
use hsm_kernel::V3;

/// The cold core's own corner fitting for its internal routes.
#[allow(dead_code)]
#[path = "../../../cold-core-layout/core_routes.rs"]
mod core_routes;

/// The fitted lines and arcs through `points`, each corner turned at the radius the cold core's
/// fitting gives it for a stock bend of `bend_radius`, in source order.
pub fn route_segments(points: &[[f64; 3]], bend_radius: f64) -> Result<Vec<Segment>> {
    let source: Vec<V3> = points.iter().map(|&p| V3::from(p)).collect();
    let (points, radii) = core_routes::corner_radii(&source, bend_radius)?;
    let mut segments = Vec::new();
    let mut tail = points[0];
    let line = |from: V3, to: V3| Segment::Line {
        start_mm: from.to_array(),
        end_mm: to.to_array(),
        length_mm: (to - from).norm(),
    };
    for i in 1..points.len() - 1 {
        let u = (points[i - 1] - points[i]).unit();
        let w = (points[i + 1] - points[i]).unit();
        let half = acos(u.dot(w).clamp(-1., 1.)) / 2.;
        let setback = radii[i] / tan(half);
        let incoming = points[i] + u * setback;
        let outgoing = points[i] + w * setback;
        let centre = points[i] + (u + w).unit() * (radii[i] / sin(half));
        let mid = centre + (points[i] - centre).unit() * radii[i];
        if (incoming - tail).norm() > 1e-7 {
            segments.push(line(tail, incoming));
        }
        let angle = std::f64::consts::PI - 2. * half;
        segments.push(Segment::Arc {
            start_mm: incoming.to_array(),
            midpoint_mm: mid.to_array(),
            end_mm: outgoing.to_array(),
            radius_mm: radii[i],
            angle_radians: angle,
            length_mm: radii[i] * angle,
        });
        tail = outgoing;
    }
    let last = points[points.len() - 1];
    if (last - tail).norm() > 1e-7 {
        segments.push(line(tail, last));
    }
    Ok(segments)
}
