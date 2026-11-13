//! The Industrial faucet's assembly with its shell base and counter mounting stack under the
//! head both styles share.
//!
//!     faucet-industrial-assembly [<output directory>]
fn main() -> anyhow::Result<()> {
    hsm_faucet_assembly::run(hsm_faucet_assembly::Variant::Industrial)
}
