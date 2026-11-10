//! The elbow reference preserves measured socket landmarks with smooth molded lands and rounds.
use anyhow::{Context, Result};
use hsm_kernel::{Body, Loop, Plane, Profile, Seg, Solid, V2, V3, part, v2, v3};
use std::path::PathBuf;

const TUBE_RADIUS: f64 = 3.175;
const COLLET_FACE: f64 = 20.56239;
const FIXED_FACE: f64 = 18.837;
const CORE_RADIUS: f64 = 4.05;
const WEB_WIDTH: f64 = 5.16;
const WEB_SIDE: f64 = 7.57;
const WEB_CENTER: f64 = -0.285;
const WEB_RADIUS: f64 = 1.25;

/// The hidden socket shares the exposed shape with its independently measured diameter offsets.
fn socket_point(t: f64, r: f64, hidden: bool) -> V2 {
    const OFFSETS: [(f64, f64); 7] = [
        (2.5, 0.), (6.7, -0.025), (8.3, -0.05124), (10.8, -0.05124),
        (13.6, -0.07293), (15.8, -0.07293), (FIXED_FACE, 0.),
    ];
    let correction = if !hidden || t <= OFFSETS[0].0 {
        0.
    } else {
        OFFSETS.windows(2).find(|w| t <= w[1].0).map_or(0., |w| {
            w[0].1 + (w[1].1 - w[0].1) * (t - w[0].0) / (w[1].0 - w[0].0)
        })
    };
    v2(t, r + correction)
}

fn fixed_profile(hidden: bool) -> Result<Profile> {
    let p = |t, r| socket_point(t, r, hidden);
    let axis_start = v2(2.5, 0.);
    let a = p(2.5, 4.08);
    let b = p(4., 4.667);
    let c = p(6.6, 4.7117);
    let d = p(6.963, 4.92);
    let e = p(6.963, 5.98);
    let f = p(8., 6.819);
    let g = p(10.9, 6.888);
    let h = p(13.2, 8.116);
    let i = p(15.75, 8.1657);
    let j = p(16.562, 7.65);
    let k = p(16.562, 7.33);
    let l = p(17., 7.0882);
    let m = p(FIXED_FACE, 6.06);
    let axis_end = v2(FIXED_FACE, 0.);
    Ok(Profile::new(Loop::new(vec![
        Seg::Line { a: axis_start, b: a },
        Seg::Cubic { a, c1: p(3.25, 4.32), c2: p(3.3, 4.655), b },
        Seg::Line { a: b, b: c },
        Seg::Cubic { a: c, c1: p(6.85, 4.716), c2: p(6.963, 4.8), b: d },
        Seg::Line { a: d, b: e },
        Seg::Cubic { a: e, c1: p(6.963, 6.), c2: p(7.24275, 6.80111), b: f },
        Seg::Line { a: f, b: g },
        Seg::Cubic { a: g, c1: p(11.8594, 6.91067), c2: p(12.07016, 8.09399), b: h },
        Seg::Line { a: h, b: i },
        Seg::Cubic { a: i, c1: p(16.2028, 8.17452), c2: p(16.562, 7.97652), b: j },
        Seg::Line { a: j, b: k },
        Seg::Cubic { a: k, c1: p(16.562, 7.21384), c2: p(16.90815, 7.05146), b: l },
        Seg::Cubic { a: l, c1: p(18.70858, 7.77163), c2: p(FIXED_FACE, 6.061), b: m },
        Seg::Line { a: m, b: axis_end },
        Seg::Line { a: axis_end, b: axis_start },
    ])?))
}

/// The release ring keeps its measured taper, rounded rim and resting face.
fn collet_profile() -> Result<Profile> {
    let a = v2(FIXED_FACE, 0.);
    let b = v2(FIXED_FACE, 5.30);
    let c = v2(20., 5.21);
    let d = v2(COLLET_FACE, 4.73);
    let e = v2(COLLET_FACE, 0.);
    Ok(Profile::new(Loop::new(vec![
        Seg::Line { a, b },
        Seg::Line { a: b, b: c },
        Seg::Cubic { a: c, c1: v2(20.35, 5.183), c2: v2(COLLET_FACE, 5.02), b: d },
        Seg::Line { a: d, b: e },
        Seg::Line { a: e, b: a },
    ])?))
}

fn socket(profile: &Profile, hidden: bool) -> Result<Solid> {
    let axial = Plane::XY.revolve(profile, 360., V2::ZERO, v2(1., 0.))?;
    Ok(if hidden {
        axial.rotate(V3::ZERO, V3::Y, -90.)
    } else {
        axial.rotate(V3::ZERO, V3::Z, 90.)
    })
}

fn srgb(c: [f64; 3]) -> [f64; 3] {
    c.map(|x| if x <= 0.04045 { x / 12.92 } else { ((x + 0.055) / 1.055).powf(2.4) })
}

fn main() -> Result<()> {
    let out = PathBuf::from(std::env::args().nth(1).context("reference output directory")?);
    std::fs::create_dir_all(&out)?;
    let web = Plane::YZ.at(v3(-WEB_WIDTH / 2., 0., 0.)).extrude(
        &Profile::new(Loop::rounded_rect(v2(WEB_CENTER, WEB_CENTER), WEB_SIDE, WEB_SIDE, WEB_RADIUS)?),
        WEB_WIDTH,
    )?;
    let mut core = Solid::sphere(V3::ZERO, CORE_RADIUS)?.union(&web)?;
    for axis in [V3::Y, V3::Z] {
        core = core.union(&Solid::cylinder(V3::ZERO, axis, CORE_RADIUS, 3.5)?)?;
    }
    let collet = collet_profile()?;
    let mut rings = Vec::new();
    for hidden in [false, true] {
        let axis = if hidden { V3::Z } else { V3::Y };
        core = core.union(&socket(&fixed_profile(hidden)?, hidden)?)?;
        // The nominal tube corridor establishes no insertion stop or internal mechanism.
        let bore = Solid::cylinder(V3::ZERO, axis, TUBE_RADIUS, 24.)?;
        rings.push(socket(&collet, hidden)?.cut(&bore)?);
    }
    for axis in [V3::Y, V3::Z] {
        core = core.cut(&Solid::cylinder(V3::ZERO, axis, TUBE_RADIUS, 24.)?)?;
    }
    let bodies = [
        Body { name: "fixed_body", color: Some(srgb([0.20, 0.24, 0.28])), solid: &core },
        Body { name: "y_collet", color: Some(srgb([0.50, 0.56, 0.59])), solid: &rings[0] },
        Body { name: "z_collet", color: Some(srgb([0.50, 0.56, 0.59])), solid: &rings[1] },
    ];
    println!("{}", part::write_shown(&out, "jg-pp0308e-elbow", &bodies)?);
    Ok(())
}
