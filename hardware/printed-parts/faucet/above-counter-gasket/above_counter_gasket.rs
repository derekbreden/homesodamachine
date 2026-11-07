//! The Sculpted faucet's above-counter gasket: its oval foot in black TPU with the shank hole, the
//! flavor pill and the cable lane through it.
//!
//!     above-counter-gasket [<output directory>]
use anyhow::{Result, ensure};
use hsm_faucet::counter;
use hsm_faucet_numbers::catalog;
use hsm_kernel::Body;
use hsm_print_payload::printed;

const NAME: &str = "above-counter-gasket";

fn main() -> Result<()> {
    let out = printed::out_dir("hardware/printed-parts/faucet/above-counter-gasket")?;
    let gasket = counter::gasket(counter::oval)?;
    ensure!(gasket.components().len() == 1, "the above-counter gasket is not one solid");
    let body = Body { name: NAME, color: Some(catalog::tpu_black()), solid: &gasket };
    println!("{}", printed::write(&out, NAME, body)?);
    Ok(())
}
