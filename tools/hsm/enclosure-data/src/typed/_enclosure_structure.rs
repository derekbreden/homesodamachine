//! Rust construction datums for the enclosure's swept exterior.
//!
//! Numbers for the enclosure's swept structural exterior, shared with its native builders:
//! `swept-structure` (`core_profiles`), answered in this process from `_swept_top`'s parameters
//! as they stand at the call, and handed out as `_enclosure_core_data.tupled` hands them.
use super::py::{self, Val};
use super::rt::{Ns, Rt};
use anyhow::Result;
use serde_json::json;
use std::rc::Rc;

pub const TYPED: bool = true;
const MODULE: &str = "_enclosure_structure";

pub struct State {
    /// `overhang_round.OUTWARD_PER_HEIGHT`.
    outward_per_height: serde_json::Value,
}

pub fn state(rt: &Rt) -> Result<Rc<State>> {
    rt.state::<State>(MODULE)
}

pub fn install(rt: &Rt, ns: &Ns) -> Result<()> {
    ns.set("_swept_top", rt.import("_swept_top")?)?;
    let slope = rt.member("overhang_round", "OUTWARD_PER_HEIGHT")?;
    ns.set("OUTWARD_PER_HEIGHT", slope.clone())?;
    ns.set("read", rt.member("_enclosure_data", "read")?)?;
    ns.set("tupled", rt.member("_enclosure_core_data", "tupled")?)?;
    rt.keep(MODULE, State { outward_per_height: py::plain(&slope)? });
    ns.def(rt, "numbers", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["outer"], &[])?;
        numbers(rt, &b.req("outer")?)
    })?;
    Ok(())
}

pub fn main_block(_rt: &Rt) -> Result<()> {
    Ok(())
}

/// The exact display profile and print-down roof sections; no native geometry is built.
pub fn numbers(rt: &Rt, outer: &Val) -> Result<Val> {
    let slope = state(rt)?.outward_per_height.clone();
    let parameters = py::plain(&super::_swept_top::parameters(rt)?)?;
    let reading = rt.enclosure_data(json!({"op": "swept-structure", "outer": py::plain(outer)?,
        "parameters": parameters, "outward_per_height": slope}))?;
    super::_swept_top::tupled(reading)
}
