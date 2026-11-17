//! Models the gray John Guest male connector for the parts catalog.
use anyhow::Result;
use hsm_kernel::{Body, Loop, Plane, Profile, Solid, V2, V3, part, v2};
use hsm_sandbox::{material, out};

const NAME: &str = "jg-pi010822s";
const TUBE_RADIUS: f64 = 6.35 / 2.;
const INSERTION_DEPTH: f64 = 15.7;
const THREAD_SHOULDER: f64 = 13.7;
const THREAD_LENGTH: f64 = 14.3;
const FLOW_RADIUS: f64 = 4.4 / 2.;
const HEX_FLATS: f64 = 17.5;
const MAX_BODY_RADIUS: f64 = 19.1 / 2.;
const LENGTH: f64 = THREAD_SHOULDER + THREAD_LENGTH;

const THREAD_PITCH: f64 = 25.4 / 18.;
const THREAD_MAJOR_RADIUS: f64 = 0.540 * 25.4 / 2.;
const THREAD_RADIUS_TAPER: f64 = 1. / 32.;

fn turned(section: &[(f64, f64)]) -> Result<Solid> {
    let points: Vec<_> = section.iter().map(|&(r, z)| v2(r, z)).collect();
    Plane::XZ.revolve(&Profile::polygon(&points), 360., V2::ZERO, v2(0., 1.))
}

fn thread_groove() -> Result<Solid> {
    let start = THREAD_SHOULDER + 0.65 * THREAD_PITCH;
    let turns = (LENGTH + THREAD_PITCH - start) / THREAD_PITCH;
    let root = THREAD_MAJOR_RADIUS - THREAD_LENGTH * THREAD_RADIUS_TAPER / 2. - 0.70 * THREAD_PITCH;
    let root_half_width = 0.045 * THREAD_PITCH;
    let outer_half_width = 0.48 * THREAD_PITCH;
    let flank_end = root + (outer_half_width - root_half_width) * 3_f64.sqrt();
    let outside = THREAD_MAJOR_RADIUS + 0.3;
    let groove = Profile::polygon(&[
        v2(root, start - root_half_width),
        v2(flank_end, start - outer_half_width),
        v2(outside, start - outer_half_width),
        v2(outside, start + outer_half_width),
        v2(flank_end, start + outer_half_width),
        v2(root, start + root_half_width),
    ]);
    Plane::XZ.screw(&groove, V3::ZERO, V3::Z, THREAD_PITCH, turns)
}

fn body() -> Result<Solid> {
    let thread_tip = THREAD_MAJOR_RADIUS - THREAD_LENGTH * THREAD_RADIUS_TAPER;
    let body = turned(&[
        (7.65, 1.95),
        (7.95, 2.25),
        (7.95, 3.35),
        (7.75, 3.35),
        (7.75, 4.05),
        (8.45, 4.05),
        (8.45, 8.65),
        (MAX_BODY_RADIUS, 9.35),
        (MAX_BODY_RADIUS, THREAD_SHOULDER - 0.4),
        (8.65, THREAD_SHOULDER),
        (7.15, THREAD_SHOULDER),
        (THREAD_MAJOR_RADIUS - 0.4 * THREAD_RADIUS_TAPER, THREAD_SHOULDER + 0.4),
        (thread_tip + 0.6 * THREAD_RADIUS_TAPER, LENGTH - 0.6),
        (thread_tip - 0.6, LENGTH),
        (FLOW_RADIUS + 0.4, LENGTH),
        (FLOW_RADIUS, LENGTH - 0.4),
        (FLOW_RADIUS, INSERTION_DEPTH),
        (TUBE_RADIUS, INSERTION_DEPTH),
        (TUBE_RADIUS, 7.4),
        (4.7, 6.5),
        (4.7, 1.95),
    ])?;

    let hex = Profile::new(Loop::regular(V2::ZERO, 6, HEX_FLATS / (3_f64.sqrt() / 2.)));
    let wrench_flats = Plane::XY.extrude(&hex, LENGTH + 1.)?;
    body.intersect(&wrench_flats)?.cut(&thread_groove()?)
}

fn collet() -> Result<Solid> {
    turned(&[
        (6.16, 0.),
        (6.42, 0.26),
        (6.42, 1.05),
        (4.3, 1.05),
        (4.3, 2.4),
        (4.58, 3.15),
        (4.58, 5.6),
        (4.3, 6.15),
        (TUBE_RADIUS, 6.15),
        (TUBE_RADIUS, 0.42),
        (3.6, 0.),
    ])
}

fn main() -> Result<()> {
    let body = body()?.rotate(V3::ZERO, V3::Y, 90.);
    let collet = collet()?.rotate(V3::ZERO, V3::Y, 90.);
    let bodies = [
        Body { name: "body", color: Some(material("M_JG_GREY_ACETAL")?), solid: &body },
        Body { name: "collet", color: Some([0.09, 0.11, 0.14]), solid: &collet },
    ];
    println!("{}", part::write_shown(&out()?, NAME, &bodies)?);
    Ok(())
}
