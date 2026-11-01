//! Cut-stock barrel, on its saw datum, from `carbonator_tube_step.py`.
#[path = "../round_stock.rs"]
mod round_stock;

fn main() -> anyhow::Result<()> { round_stock::main() }
