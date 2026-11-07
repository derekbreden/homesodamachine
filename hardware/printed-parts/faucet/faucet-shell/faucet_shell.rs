//! The faucet shell: the printed shroud round the harvested Westbrass, the flavor tubes and the
//! lever's swing, its gooseneck carrying the tubes to the glass and the display on its tip. It
//! prints in two pieces split across the bend, the tip's plug sliding into the base's socket; each
//! piece's STEP, model, STL and payload.
//!
//!     faucet-shell [<output directory>]
use anyhow::Result;
use hsm_faucet::Gooseneck;
use hsm_faucet::shell::{pieces, shell};
use hsm_faucet_numbers::catalog;
use hsm_kernel::Body;
use hsm_print_payload::printed;

fn main() -> Result<()> {
    let out = printed::out_dir("hardware/printed-parts/faucet/faucet-shell")?;
    let neck = Gooseneck::shell();
    let (base, tip) = pieces(&neck, &shell(&neck)?)?;
    let color = Some(catalog::faucet_black());
    for (name, solid) in [("faucet-shell-base", &base), ("faucet-shell-tip", &tip)] {
        println!("{}", printed::write(&out, name, Body { name, color, solid })?);
    }
    Ok(())
}
