//! The Sculpted faucet's above-counter gasket on the kernel: its oval foot with the shank hole,
//! the flavor pill and the cable lane through it. `above_counter_gasket.py` holds the numbers and
//! writes them for this program.
//!
//!     cargo run --release --manifest-path tools/hsm/faucet/Cargo.toml --bin above-counter-gasket -- \
//!         <above-counter-gasket.numbers.json> <out dir>
use anyhow::{Result, ensure};
use hsm_faucet::counter;
use hsm_kernel::part::{args, write_printed};
use hsm_kernel::*;

fn main() -> Result<()> {
    let (n, out) = args()?;
    let gasket = counter::gasket(&n, |z0, z1| counter::oval(&n, z0, z1))?;
    ensure!(gasket.components().len() == 1, "the above-counter gasket is not one solid");
    let name = n.text("name")?;
    println!("{}", write_printed(&out, name, &[Body { name, color: Some(n.color("color")?), solid: &gasket }])?);
    Ok(())
}
