//! The Sculpted faucet's above-counter plate: its oval foot with a pedestal under each mounting pod,
//! bored and counterbored for the pod's screw, and the shank hole, the flavor pill and the cable
//! lane through it.
//!
//!     above-counter-plate [<output directory>]
use anyhow::{Result, ensure};
use hsm_faucet::counter;
use hsm_faucet_numbers::catalog;
use hsm_kernel::Body;
use hsm_print_payload::printed;

const NAME: &str = "above-counter-plate";

fn main() -> Result<()> {
    let out = printed::out_dir("hardware/printed-parts/faucet/above-counter-plate")?;
    let plate = counter::plate(counter::oval)?;
    ensure!(plate.components().len() == 1, "the above-counter plate is not one solid");
    let body = Body { name: NAME, color: Some(catalog::faucet_black()), solid: &plate };
    println!("{}", printed::write(&out, NAME, body)?);
    Ok(())
}
