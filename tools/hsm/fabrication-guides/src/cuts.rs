//! The bench guide reads the factory cuts from the faucet assembly's authored centrelines.
use anyhow::Result;
use hsm_faucet_assembly::cuts;
use hsm_faucet_assembly_numbers as assembly;
use serde::Serialize;

#[derive(Serialize)]
pub struct FaucetCuts {
    pub blue_cut: f64,
    pub flavor_cut: f64,
    pub soda_faucet_cut: f64,
    pub drain_cut: f64,
    pub foam_length: f64,
    pub foam_bare_top: f64,
    pub collar_sleeve_tail: f64,
}

pub fn faucet() -> Result<FaucetCuts> {
    let foam_bare_top = assembly::SODA_UMBILICAL_TUBE_Z_TOP - assembly::foam_z_top();
    Ok(FaucetCuts {
        blue_cut: assembly::BLUE_CUT_LENGTH,
        flavor_cut: cuts::flavor()?,
        soda_faucet_cut: cuts::soda_faucet()?,
        drain_cut: cuts::drain_factory()?,
        foam_length: assembly::BLUE_CUT_LENGTH - foam_bare_top - assembly::FOAM_BARE_AT_WALL,
        foam_bare_top,
        collar_sleeve_tail: assembly::FOAM_BARE_AT_WALL,
    })
}
