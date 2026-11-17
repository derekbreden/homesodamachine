//! The stiffener reference shows the flanged sleeve that supports the soda supply tube.
use anyhow::Result;
use hsm_kernel::{Pen, Plane, Profile, Solid, V2, v2};
use hsm_sandbox::{material, out, show};

const LENGTH: f64 = 13.0;
const FLANGE_RADIUS: f64 = 6.35 / 2.0;
const STEM_RADIUS: f64 = 4.2 / 2.0;
const WALL: f64 = 0.17;
const FLARE_RADIUS: f64 = 0.12;
const LEAD_IN: f64 = 0.05;

fn stiffener() -> Result<Solid> {
    let bore = STEM_RADIUS - WALL;
    let flare_rim = STEM_RADIUS + FLARE_RADIUS;
    let flare_start = LENGTH - FLARE_RADIUS - WALL;
    let flare_center = v2(flare_rim, flare_start);
    let rim_round = WALL / 2.0;
    let rim_land = FLANGE_RADIUS - rim_round;

    let section = Pen::new(v2(bore, 0.0))
        .line_to(v2(STEM_RADIUS - LEAD_IN, 0.0))
        .line_to(v2(STEM_RADIUS, LEAD_IN))
        .line_to(v2(STEM_RADIUS, flare_start))
        .arc_center(flare_center, v2(flare_rim, LENGTH - WALL), false)
        .line_to(v2(rim_land, LENGTH - WALL))
        .arc_center(v2(rim_land, LENGTH - rim_round), v2(rim_land, LENGTH), true)
        .line_to(v2(flare_rim, LENGTH))
        .arc_center(flare_center, v2(bore, flare_start), true)
        .close()?;

    Plane::XZ.revolve(&Profile::new(section), 360.0, V2::ZERO, v2(0.0, 1.0))
}

fn main() -> Result<()> {
    let dir = out()?;
    let insert = stiffener()?;
    show(
        &dir,
        "siptenk-tube-stiffener",
        &[("brass sleeve", material("M_BRASS")?, &insert)],
    )
}
