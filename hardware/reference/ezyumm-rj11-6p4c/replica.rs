//! The modular plug reference draws the molded shell and the loose plug's gold contact blades.
use anyhow::Result;
use hsm_kernel::{Body, Loop, Plane, Profile, Solid, part, v2, v3};

const NAME: &str = "ezyumm-rj11-6p4c";

const BODY_WIDTH: f64 = 9.65;
const BODY_LENGTH: f64 = 12.30;
const BODY_HEIGHT: f64 = 6.60;
const BODY_CORNER: f64 = 0.42;
const NOSE_Y: f64 = -1.00;
const LATCH_BASE_WIDTH: f64 = 6.10;
const LATCH_TONGUE_WIDTH: f64 = 3.25;
const LATCH_CATCH_Y: f64 = 1.02 + 5.89;
const LATCH_CATCH_Z: f64 = BODY_HEIGHT + 2.77;
const PITCH: f64 = 1.02;
const BLADE_THICKNESS: f64 = 0.51;
const BLADE_SLOT_WIDTH: f64 = 0.56;
const ENTRY_WIDTH: f64 = 5.50;
const ENTRY_HEIGHT: f64 = 3.10;
const ENTRY_CENTER_Z: f64 = 3.46;
const WIRE_CHANNEL_DIAMETER: f64 = 1.00;
const CONTACT_OUTLINE: &[(f64, f64)] = &[
    (0.36, -0.64), (4.10, -0.64), (4.37, -0.40),
    (4.45, -0.16), (4.45, 0.94), (3.90, 0.94),
    (3.78, 1.10), (3.78, 1.66), (3.98, 1.74),
    (3.95, 3.20), (3.81, 3.63), (3.64, 3.77),
    (3.49, 3.68), (3.42, 2.97), (3.28, 2.72),
    (2.86, 2.72), (2.74, 2.91), (2.67, 3.48),
    (2.49, 3.68), (2.31, 3.61), (2.19, 3.40),
    (2.12, 2.90), (1.99, 2.72), (1.60, 2.72),
    (1.46, 2.89), (1.41, 3.58), (1.28, 3.76),
    (1.08, 3.71), (0.92, 3.41), (0.81, 2.97),
    (0.81, 1.79), (1.01, 1.68), (1.01, 1.08),
    (0.85, 0.94), (0.09, 0.94), (0.09, -0.32),
    (0.18, -0.49),
];

fn side_profile(points: &[(f64, f64)], x: f64, width: f64) -> Result<Solid> {
    let outline = points.iter().map(|&(y, z)| v2(y, z)).collect::<Vec<_>>();
    Plane::YZ.at(v3(x - width / 2., 0., 0.))
        .extrude(&Profile::polygon(&outline), width)
}

fn position(index: u8) -> f64 {
    (f64::from(index) - 3.5) * PITCH
}

fn housing() -> Result<Solid> {
    let shell = Plane::XY.extrude(
        &Profile::new(Loop::rounded_rect(
            v2(0., BODY_LENGTH / 2.), BODY_WIDTH, BODY_LENGTH, BODY_CORNER,
        )?),
        BODY_HEIGHT,
    )?;
    let latch_base = side_profile(&[
        (NOSE_Y, 4.48), (1.02, 4.48), (1.02, 6.48), (2.56, 6.48),
        (2.56, 7.12), (LATCH_CATCH_Y, 8.18), (LATCH_CATCH_Y, LATCH_CATCH_Z),
        (5.46, 9.04), (4.67, 8.22), (2.75, 7.83), (-0.62, 7.83), (NOSE_Y, 7.45),
    ], 0., LATCH_BASE_WIDTH)?;
    let latch_tongue = side_profile(&[
        (4.36, 7.78), (13.37, 9.65), (13.66, 9.84), (13.66, 10.88),
        (13.38, 11.02), (4.36, 8.81),
    ], 0., LATCH_TONGUE_WIDTH)?;

    let mut shell = shell.union(&latch_base)?.union(&latch_tongue)?;
    let entry = Plane::XZ.at(v3(0., BODY_LENGTH + 0.1, ENTRY_CENTER_Z)).extrude(
        &Profile::new(Loop::rounded_rect(v2(0., 0.), ENTRY_WIDTH, ENTRY_HEIGHT, 0.34)?),
        6.17,
    )?;
    let relief_window = Solid::cuboid(v3(-2.82, 6.85, -0.1), v3(2.82, 10.44, 2.24));
    shell = shell.cut(&entry)?.cut(&relief_window)?;
    let relief_bar = side_profile(&[
        (7.71, 1.83), (8.19, 0.64), (10.62, 0.9), (10.62, 1.76), (9.81, 2.05),
    ], 0., 5.15)?;
    shell = shell.union(&relief_bar)?;

    let mut contact_cuts = Vec::new();
    for pin in 1..=6 {
        let x = position(pin);
        contact_cuts.push(side_profile(&[
            (-0.15, -0.14), (5.33, -0.14), (5.33, 2.62), (4.08, 2.91),
            (4.08, 3.90), (0.66, 3.90), (0.66, 2.60), (-0.15, 2.60),
        ], x, BLADE_SLOT_WIDTH)?);
        contact_cuts.push(Plane::XZ.at(v3(x, 6.63, ENTRY_CENTER_Z)).extrude(
            &Profile::circle(v2(0., 0.), WIRE_CHANNEL_DIAMETER / 2.), 5.28,
        )?);
    }
    shell.cut_all(&contact_cuts)
}

fn blade(pin: u8) -> Result<Solid> {
    side_profile(CONTACT_OUTLINE, position(pin), BLADE_THICKNESS)
}

fn contact_side_up(solid: Solid) -> Solid {
    solid.rotate(v3(0., 0., 0.), v3(0., 1., 0.), 180.)
}

fn main() -> Result<()> {
    let dir = hsm_sandbox::out()?;
    let housing = contact_side_up(housing()?);
    let neutral = hsm_sandbox::material("M_PVC_CLEAR")?;
    let gold = [0.77, 0.46, 0.10];
    let mut bodies = vec![Body { name: "plug-housing", color: Some(neutral), solid: &housing }];
    let blades = (2..=5).map(|pin| blade(pin).map(contact_side_up))
        .collect::<Result<Vec<_>>>()?;
    for (name, solid) in ["contact-2", "contact-3", "contact-4", "contact-5"].into_iter().zip(&blades) {
        bodies.push(Body { name, color: Some(gold), solid });
    }
    println!("{}", part::write_shown(&dir, NAME, &bodies)?);
    Ok(())
}
