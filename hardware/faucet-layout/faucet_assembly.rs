//! The Sculpted faucet's assembly: its STEP, model file and payload.
//!
//!     faucet-assembly [<output directory>]
fn main() -> anyhow::Result<()> {
    hsm_faucet_assembly::run(hsm_faucet_assembly::Variant::Sculpted)
}
