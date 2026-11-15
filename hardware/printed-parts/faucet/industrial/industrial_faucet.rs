//! The Industrial faucet: the shell's gooseneck and cutters on round stock of its own below the
//! zone-5 seam (a foot disc, a body over the Westbrass and the neck standing on it), and its round
//! above-counter plate and gasket.
//!
//!     industrial-faucet [<output directory>]
use anyhow::{Result, ensure};
use hsm_faucet::shell::{level, pieces, shell_from};
use hsm_faucet::{Gooseneck, counter};
use hsm_faucet_numbers::catalog;
use hsm_faucet_numbers::shell::*;
use hsm_industrial_faucet_numbers as industrial;
use hsm_kernel::*;
use hsm_print_payload::printed;

fn main() -> Result<()> {
    let out = printed::out_dir("hardware/printed-parts/faucet/industrial")?;
    let neck = Gooseneck::shell();
    let black = Some(catalog::faucet_black());
    // The round foot the plate and gasket share.
    let disc = |z0: f64, z1: f64| Solid::cylinder(v3(0.0, 0.0, z0), V3::Z, industrial::FOOT_RADIUS, z1 - z0);
    let printed_pieces = [
        ("industrial-shell-base", shell_base(&neck)?, black),
        ("industrial-above-counter-plate", counter::plate(disc)?, black),
        ("industrial-above-counter-gasket", counter::gasket(disc)?, Some(catalog::tpu_black())),
    ];
    for (name, solid, color) in &printed_pieces {
        ensure!(solid.components().len() == 1, "{name} is not one solid");
        println!("{}", printed::write(&out, name, Body { name, color: *color, solid })?);
    }
    Ok(())
}

/// The base: the shell's gooseneck and cutters on the Industrial's own stock below the seam, its
/// lever corridor carried up to the top of the body, split from the tip as the shell is.
fn shell_base(neck: &Gooseneck) -> Result<Solid> {
    let (foot_top, body_top, seam) = (industrial::FOOT_TOP, industrial::BODY_TOP, ZONE5_Z_TOP);
    let foot = Solid::cylinder(V3::ZERO, V3::Z, industrial::FOOT_RADIUS, foot_top)?;
    let body = Solid::cylinder(v3(0.0, industrial::BODY_CENTER_Y, foot_top), V3::Z, industrial::BODY_RADIUS, body_top - foot_top)?;
    let ring = Profile::circle(v2(0.0, industrial::NECK_CENTER_Y), industrial::NECK_RADIUS);
    let stem = level(body_top).extrude(&ring, seam + industrial::NECK_JOIN_OVERLAP - body_top)?;
    let stock = Solid::union_all(&[foot, body, stem])?;
    let xh = LEVER_CLEARANCE_X_HALF;
    let lever = Solid::cuboid(v3(-xh, LEVER_INSERTION_FRONT_Y, LEVER_REST_TOP_Z), v3(xh, FILL_Y_MIN, body_top));
    let full = shell_from(neck, stock, &ring.place(&level(seam)), &[lever])?;
    Ok(pieces(neck, &full)?.0)
}
