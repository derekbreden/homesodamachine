#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    let assigned1 = Val::Float(9.5f64);
    e.set("JET_CAP_D", assigned1.clone())?;
    let assigned2 = Val::Float(2.0f64);
    e.set("JET_CAP_T", assigned2.clone())?;
    let assigned3 = binary("truediv", Val::Float(25.4f64), Val::Float(16.0f64))?;
    e.set("JET_PASSAGE_D", assigned3.clone())?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    Ok(Val::None)
}
