//! Scalar dimensions on the faucet's kernel paths and analytic circle hulls.
use anyhow::{Context, Result};
use hsm_kernel::part::Numbers;

fn main() -> Result<()> {
    let input = std::env::args().nth(1).context("usage: faucet-metrics <numbers.json>")?;
    let numbers = Numbers::read(input)?;
    println!("{}", hsm_faucet::metrics::measure(&numbers)?);
    Ok(())
}
