//! The Sculpted faucet's assembly: its STEP, model file and payload, and the countertop the
//! install guide's opening scene holds the faucet's tails over.
//!
//!     faucet-assembly [<output directory>]
fn main() -> anyhow::Result<()> {
    hsm_faucet_assembly::run(hsm_faucet_assembly::Variant::Sculpted)
}
