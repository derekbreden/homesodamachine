//! The one-piece acetal turning carries the shutoff face, balance piston, rod guide land and dry pull eye.
use super::*;
use std::f64::consts::{FRAC_PI_2, PI};

pub const STEM_R: f64 = 1.50;
pub const CROWN_R: f64 = 0.26;
pub const GUIDE_R: f64 = STEM_R + 0.055;
pub const GLAND_R: f64 = STEM_R + 0.85;
pub const GUIDE_IN: f64 = 15.18;
pub const GLAND_START: f64 = 15.46;
pub const GLAND_END: f64 = GLAND_START + 1.28;
pub const GUIDE_END: f64 = GLAND_END + 0.20;
const SHOULDER: f64 = 17.44;
const WASHER_THICKNESS: f64 = 0.49;
const FLAT: f64 = 0.70;
const FLAT_FILLET: f64 = 0.20;
const PIN_R: f64 = 0.775;
pub const SPRING_FRONT: f64 = SHOULDER + WASHER_THICKNESS;

fn arc(profile: &mut Vec<(f64, f64)>, r: f64, s: f64, radius: f64, start: f64, end: f64) {
    for i in 0..=12 {
        let t = start + (end - start) * f64::from(i) / 12.;
        profile.push((r + radius * t.cos(), s + radius * t.sin()));
    }
}

pub fn turning() -> Result<Solid> {
    let crown = front_seat::SEAT_D / 2.;
    let seat = front_seat::SEAT_S;
    let end = PIN_S + 2.28;
    let mut profile = vec![(0., seat + CROWN_R)];
    arc(&mut profile, crown, seat + CROWN_R, CROWN_R, PI, 2. * PI);
    profile.extend([(crown + CROWN_R, 1.47), (crown + CROWN_R - 0.10, 1.57)]);
    arc(&mut profile, STEM_R + 0.36, 1.93, 0.36, -FRAC_PI_2, -PI);
    arc(&mut profile, STEM_R + 0.25, balance::PISTON_S - 0.25, 0.25, PI, FRAC_PI_2);
    let groove = balance::PISTON_SEAL_S - balance::PISTON_GROOVE_WIDTH / 2.;
    let end_groove = groove + balance::PISTON_GROOVE_WIDTH;
    let piston_r = balance::PISTON_R;
    let root = balance::PISTON_GROOVE_R;
    profile.extend([
        (piston_r - 0.09, balance::PISTON_S),
        (piston_r, balance::PISTON_S + 0.11),
        (piston_r, groove - 0.045),
        (piston_r - 0.045, groove),
    ]);
    arc(&mut profile, root + 0.05, groove + 0.05, 0.05, -FRAC_PI_2, -PI);
    arc(&mut profile, root + 0.05, end_groove - 0.05, 0.05, PI, FRAC_PI_2);
    profile.extend([
        (piston_r - 0.045, end_groove),
        (piston_r, end_groove + 0.045),
        (piston_r, balance::PISTON_END_S - 0.11),
        (piston_r - 0.09, balance::PISTON_END_S),
    ]);
    arc(&mut profile, STEM_R + 0.22, balance::PISTON_END_S + 0.22, 0.22, -FRAC_PI_2, -PI);
    profile.extend([(STEM_R, end - 0.30), (STEM_R - 0.30, end), (0., end)]);
    let round = turn(&profile)?;
    let mut flat_profile = vec![(3., SHOULDER)];
    arc(&mut flat_profile, FLAT + FLAT_FILLET, SHOULDER + FLAT_FILLET, FLAT_FILLET, -FRAC_PI_2, -PI);
    flat_profile.extend([(FLAT, end + 0.1), (3., end + 0.1)]);
    let outline: Vec<_> = flat_profile.iter().map(|&(x, s)| v2(x, s)).collect();
    let mill = Plane::XY.offset(-2.).extrude(&Profile::polygon(&outline), 4.)?;
    round.cut(&mill)?.cut(&mill.rotate(V3::ZERO, V3::Y, 180.))?.cut(&pin_hole(PIN_R + PIN_TRAVEL, PIN_S)?)
}

fn pin_hole(r: f64, s: f64) -> Result<Solid> {
    bore(v3(-2.85, s, 0.), v3(2.85, s, 0.), r)
}

pub fn spring_washer() -> Result<Solid> {
    let blank = axial(3.53, SHOULDER, SPRING_FRONT)?;
    let slot = Solid::cuboid(v3(-0.75, SHOULDER - 0.05, -1.59), v3(0.75, SPRING_FRONT + 0.05, 1.59));
    let relief = Solid::cuboid(v3(-0.94, SHOULDER - 0.05, -1.59), v3(0.94, SHOULDER + FLAT_FILLET, 1.59));
    blank.cut(&slot)?.cut(&relief)
}

pub fn pin_and_fork(p: &mut Vec<Piece>, lift: f64) -> Result<()> {
    let motion = V3::Y * (lift + if lift > 0. { PIN_TRAVEL } else { 0. });
    let radius = 25.4 * 0.185 / 2.;
    let hole = pin_hole(25.4 * 0.062 / 2., PIN_S)?;
    let fork = axial(radius, CLEVIS_S, MOTOR_S + 1.25)?
        .cut(&Solid::cuboid(v3(-SLOT / 2., CLEVIS_S - 0.1, -3.), v3(SLOT / 2., CLEVIS_S + 25.4 * 0.250, 3.)))?
        .cut(&hole)?;
    let pin = bore(v3(-radius, PIN_S, 0.), v3(radius, PIN_S, 0.), PIN_R)?;
    let head = |a, b| bore(v3(a, PIN_S, 0.), v3(b, PIN_S, 0.), 1.00);
    let pin = pin
        .union(&head(-radius - 0.16, -radius + 0.21)?.cut(&fork)?)?
        .union(&head(radius - 0.21, radius + 0.16)?.cut(&fork)?)?;
    add(p, "Stainless_captive_clevis_pin", STEEL, pin.translate(motion), v3(-29., 4., 0.), false);
    add(p, "Ledex_clevis_plunger", MOTOR, fork.translate(motion), V3::Y * 18., false);
    Ok(())
}

pub fn rod_seal() -> Result<Solid> {
    balance::compressed_ring(2. * STEM_R, 1.0, STEM_R, GLAND_R, (GLAND_START + GLAND_END) / 2.)
}
