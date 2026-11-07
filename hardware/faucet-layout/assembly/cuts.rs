//! The lengths the bench cuts the faucet's tubes to, off the centrelines the assembly sweeps them
//! along, each rounded up to the whole millimetre: the soda tube up the gooseneck, a flavor tube
//! from its tail into the faucet, and the drain from its tail to the vent.
use crate::legs::{self, Leg, path};
use crate::metrics::length;
use anyhow::Result;
use hsm_faucet_assembly_numbers::*;
use hsm_faucet_numbers::paths::{self, Kind};

fn along(legs: &[Leg]) -> Result<f64> {
    Ok(length(&path(legs)?))
}

/// The soda tube, from the port's floor to the tip.
pub fn soda_faucet() -> Result<f64> {
    Ok(along(&legs::soda_legs())?.ceil())
}

/// What the splay adds to a flavor tube over the straight drop from the splay's top to its tail.
fn splay_extra() -> Result<f64> {
    Ok(along(&legs::splay_legs(1.0))? - (SPLAY_TOP_Z - UMBILICAL_TAIL_Z))
}

/// A flavor tube above the pack: through the faucet and the mounting stack, over the step, round
/// the gather's two bends and down onto the pack.
fn above_pack(s: f64) -> Result<f64> {
    let faucet = along(&paths::path_legs(Kind::Flavor, UNDER_COUNTER_PLATE_BOTTOM_Z, s, None))?;
    let step = along(&legs::step_legs(s, gather_start_z()))?;
    let in_pack = (gather_start_z() - gather_rise(s)) - umbilical_z_bottom();
    Ok(faucet + step + 2.0 * UMBILICAL_BEND_RADIUS * gather_theta(s) + in_pack)
}

/// A flavor tube, both cut to the longer side's: the blue umbilical's cut less its own run above
/// the pack, what runs above the pack, and what the splay adds.
pub fn flavor() -> Result<f64> {
    let above = above_pack(1.0)?.max(above_pack(-1.0)?);
    Ok((BLUE_CUT_LENGTH + above + splay_extra()? + umbilical_z_bottom() - SODA_UMBILICAL_TUBE_Z_TOP).ceil())
}

/// The drain as the factory cuts it: the run the assembly draws, and the blue umbilical's length
/// past what it draws.
pub fn drain_factory() -> Result<f64> {
    Ok((along(&legs::drain_legs()?)? + BLUE_CUT_LENGTH - UMBILICAL_DRAWN).ceil())
}
