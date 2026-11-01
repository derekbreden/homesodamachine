//! The faucet and its umbilical on the kernel, from the display on the tip down to the four
//! square-cut tails and their collars: the sub-assembly the bench bags. `faucet_assembly.py`
//! holds the numbers and writes them for this program; `hsm_faucet::assembly` builds the bodies.
//!
//!     cargo run --release --manifest-path tools/hsm/faucet/Cargo.toml --bin faucet-assembly -- \
//!         <faucet-assembly.numbers.json> <out dir>
fn main() -> anyhow::Result<()> {
    hsm_faucet::assembly::main()
}
