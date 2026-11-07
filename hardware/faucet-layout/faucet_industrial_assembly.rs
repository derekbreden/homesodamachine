//! The Industrial faucet's assembly: the faucet assembly with the Industrial shell base,
//! above-counter plate, gasket and seated display cover standing in place of the Sculpted ones.
//!
//!     faucet-industrial-assembly [<output directory>]
fn main() -> anyhow::Result<()> {
    hsm_faucet_assembly::run(hsm_faucet_assembly::Variant::Industrial)
}
