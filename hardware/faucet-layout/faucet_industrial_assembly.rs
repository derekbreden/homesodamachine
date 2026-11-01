//! The Industrial faucet and its umbilical on the kernel: the faucet assembly with the Industrial
//! shell base, above-counter plate, gasket and seated display cover standing in place of the
//! Sculpted ones. `faucet_industrial_assembly.py` writes the numbers, the faucet assembly's own
//! with those four parts' STEPs swapped in.
//!
//!     cargo run --release --manifest-path tools/hsm/faucet/Cargo.toml --bin faucet-industrial-assembly -- \
//!         <faucet-industrial-assembly.numbers.json> <out dir>
fn main() -> anyhow::Result<()> {
    hsm_faucet::assembly::main()
}
