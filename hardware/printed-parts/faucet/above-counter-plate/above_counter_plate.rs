//! The Sculpted faucet's above-counter plate on the kernel: its oval foot with a pedestal under
//! each mounting pod, bored and counterbored for the pod's screw, and the shank hole, the flavor
//! pill and the cable lane through it. `above_counter_plate.py` holds the numbers and writes them
//! for this program.
//!
//!     cargo run --release --manifest-path tools/hsm/faucet/Cargo.toml --bin above-counter-plate -- \
//!         <above-counter-plate.numbers.json> <out dir>
use anyhow::{Result, ensure};
use hsm_faucet::counter;
use hsm_kernel::part::{args, write_printed};
use hsm_kernel::*;

fn main() -> Result<()> {
    let (n, out) = args()?;
    let plate = counter::plate(&n, |z0, z1| counter::oval(&n, z0, z1))?;
    ensure!(plate.components().len() == 1, "the above-counter plate is not one solid");
    let name = n.text("name")?;
    println!("{}", write_printed(&out, name, &[Body { name, color: Some(n.color("color")?), solid: &plate }])?);
    Ok(())
}
