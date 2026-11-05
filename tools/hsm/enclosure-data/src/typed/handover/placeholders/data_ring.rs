//! Placeholder: `data_ring` runs its generated namespace until this file holds its typed module.
#![allow(dead_code)]
use super::rt::{Ns, Rt};
use anyhow::Result;

pub const TYPED: bool = false;

pub fn install(_rt: &Rt, _ns: &Ns) -> Result<()> {
    anyhow::bail!("data_ring is not converted")
}
pub fn main_block(_rt: &Rt) -> Result<()> {
    Ok(())
}
