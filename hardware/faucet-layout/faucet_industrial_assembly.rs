//! The Industrial faucet's assembly with its shell base, counter mounting stack and approved
//! lowered display head.
//!
//!     faucet-industrial-assembly [<output directory>]
fn main() -> anyhow::Result<()> {
    hsm_faucet_assembly::run(hsm_faucet_assembly::Variant::Industrial)
}
