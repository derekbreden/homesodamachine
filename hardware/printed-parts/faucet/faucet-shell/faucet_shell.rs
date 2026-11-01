//! The faucet shell on the kernel: the printed shroud round the harvested Westbrass, the flavor
//! tubes and the lever's swing, its gooseneck carrying the tubes to the glass and the display on
//! its tip. It prints in two pieces split across the bend, the tip's plug sliding into the base's
//! socket. `faucet_shell.py` holds the numbers and writes them for this program; its builders
//! say what each feature is for.
//!
//!     cargo run --release --manifest-path tools/hsm/faucet/Cargo.toml --bin faucet-shell -- \
//!         <faucet-shell.numbers.json> <out dir>
use anyhow::{Result, ensure};
use hsm_faucet::Gooseneck;
use hsm_faucet::shell::{pieces, shell};
use hsm_kernel::Body;
use hsm_kernel::part::{args, write_printed, write_shown};

fn main() -> Result<()> {
    let (n, out) = args()?;
    let neck = Gooseneck::read(&n)?;
    let (base, tip) = pieces(&n, &neck, &shell(&n, &neck)?)?;
    for (piece, solid) in [("base", &base), ("tip", &tip)] {
        ensure!(solid.components().len() == 1, "the shell's {piece} is not one solid");
    }
    let (name, color) = (n.text("name")?, Some(n.color("color")?));
    // The assembly holds the two prints in place, the seam between them and all.
    let assembled = [Body { name: "shell_base", color, solid: &base }, Body { name: "shell_tip", color, solid: &tip }];
    println!("{}", write_shown(&out, name, &assembled)?);
    for (piece, solid) in [(format!("{name}-base"), &base), (format!("{name}-tip"), &tip)] {
        println!("{}", write_printed(&out, &piece, &[Body { name: &piece, color, solid }])?);
    }
    Ok(())
}
