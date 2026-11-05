//! Candidate inlet-jet dimensions, shared by the nominal model and fabrication procedure.

use super::*;

pub const JET_CAP_D: f64 = 9.5;
pub const JET_CAP_T: f64 = 2.0;
pub const JET_PASSAGE_D: f64 = 25.4 / 16.0;

pub fn members(_rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    ns.value("JET_CAP_D", JET_CAP_D);
    ns.value("JET_CAP_T", JET_CAP_T);
    ns.value("JET_PASSAGE_D", JET_PASSAGE_D);
    Ok(())
}

pub fn main(_rt: &Runtime) -> Result<()> {
    Ok(())
}
