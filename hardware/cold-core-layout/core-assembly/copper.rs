//! The evaporator's copper as solids: the wrap, a plain helix on the winding's circle round the
//! carbonator, and each tail's tangent form from the wrap's end to the front wall, or on past it to
//! its working stub.
use anyhow::{Context, Result};
use hsm_coil_numbers::{self as coil, Segment, Tail};
use hsm_kernel::math::{cos, radians, sin};
use hsm_kernel::*;

fn v(p: [f64; 3]) -> V3 {
    v3(p[0], p[1], p[2])
}

/// The wrap: the copper's section swept up the winding's helix from the inlet tail's azimuth.
pub fn wrap(chord: f64) -> Result<Solid> {
    let radius = coil::WIND_RADIUS;
    let angle = radians(coil::INLET_AZIMUTH);
    let start = v3(radius * cos(angle), radius * sin(angle), coil::LOW_Z);
    let pitch = coil::PITCH;
    let tangent = v3(-sin(angle) * radius, cos(angle) * radius, pitch / (2. * std::f64::consts::PI)).unit();
    let plane = Plane::new(start, V3::Z, tangent)?;
    let region = Profile::circle(V2::ZERO, coil::TUBE_RADIUS).place(&plane);
    Solid::helix_sweep_with_tolerance(&region, start, V3::Z * start.z, V3::Z, pitch, coil::WRAPS, chord)
}

/// A tail: the copper's section swept along its form's straights and bends.
pub fn tail(tail: Tail, working_tail: bool, chord: f64) -> Result<Solid> {
    let form = coil::tail_form(tail, working_tail);
    let (start, tangent) = match form.segments.first().context("a tail has segments")? {
        Segment::Bend { start, tangent, .. } => (v(*start), v(*tangent)),
        Segment::Straight { start, end, .. } => (v(*start), (v(*end) - v(*start)).unit()),
    };
    let mut path = Path::new(start);
    for segment in &form.segments {
        match segment {
            Segment::Straight { end, .. } => path = path.line_to(v(*end)),
            Segment::Bend { start, end, radius, degrees, tangent, normal, .. } => {
                let angle = radians(*degrees) / 2.;
                let mid = v(*start)
                    + v(*tangent) * (radius * sin(angle))
                    + v(*normal) * (radius * (1. - cos(angle)));
                path = path.arc_through(mid, v(*end))?;
            }
        }
    }
    let plane = Plane::new(start, V3::Z, tangent)?;
    let region = Profile::circle(V2::ZERO, coil::TUBE_RADIUS).place(&plane);
    Solid::sweep_with_tolerance(&region, &path, chord)
}
