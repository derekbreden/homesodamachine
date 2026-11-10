//! The evaporator's copper follows the authored winding over the reed bridge and each tail's
//! tangent form to the front wall, or on past it to its working stub.
use anyhow::{Context, Result};
use hsm_coil_numbers::{self as coil, Segment, Tail};
use hsm_kernel::math::{cos, radians, sin};
use hsm_kernel::*;

fn v(p: [f64; 3]) -> V3 {
    v3(p[0], p[1], p[2])
}

/// The wrap follows the authored bridge relief and retains both tails' exact end frames.
pub fn wrap(chord: f64) -> Result<Solid> {
    let (start, inlet) = first_frame(&coil::tail_form(Tail::Inlet, false))?;
    let (end, outlet) = first_frame(&coil::tail_form(Tail::Outlet, false))?;
    let count = ((coil::WRAPS * f64::from(coil::SAMPLES_PER_TURN)).round_ties_even() as usize).max(2);
    let parameters: Vec<f64> = (0..=count).map(|i| coil::WRAPS * i as f64 / count as f64).collect();
    // The spline follows the intended curve; the length ledger's polyline chord swell is omitted.
    let mut points: Vec<V3> = parameters.iter().map(|&turn| {
        let azimuth = coil::INLET_AZIMUTH + 360. * turn;
        let z = coil::LOW_Z + coil::PITCH * turn;
        v(coil::at(azimuth, z, coil::ride_radius(azimuth, z)))
    }).collect();
    points[0] = start;
    points[count] = end;
    let speed = (std::f64::consts::TAU * coil::WIND_RADIUS).hypot(coil::PITCH);
    let tangent = -inlet;
    let path = Path::new(start).clamped_spline(&points, &parameters, [tangent * speed, outlet * speed])?;
    let plane = Plane::new(start, V3::Z, tangent)?;
    let region = Profile::circle(V2::ZERO, coil::TUBE_RADIUS).place(&plane);
    Solid::sweep_with_tolerance(&region, &path, chord)
}

fn first_frame(form: &coil::TailForm) -> Result<(V3, V3)> {
    Ok(match form.segments.first().context("a tail has segments")? {
        Segment::Bend { start, tangent, .. } => (v(*start), v(*tangent)),
        Segment::Straight { start, end, .. } => (v(*start), (v(*end) - v(*start)).unit()),
    })
}

/// A tail: the copper's section swept along its form's straights and bends.
pub fn tail(tail: Tail, working_tail: bool, chord: f64) -> Result<Solid> {
    let form = coil::tail_form(tail, working_tail);
    let (start, tangent) = first_frame(&form)?;
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
