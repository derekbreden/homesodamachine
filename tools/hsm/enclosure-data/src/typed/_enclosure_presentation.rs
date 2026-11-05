//! Dispatch the enclosure's printed viewer surfaces to its Rust writer.
//!
//! Typed API: [`print_payload`] keeps the caller's print-check policy and hands the STEP to
//! [`super::_rust_enclosure_presentation::print_payload`].
use super::_rust_enclosure_presentation as presentation;
use super::py::{self, Val};
use super::rt::{Ns, Rt};
use anyhow::Result;
use std::path::{Path, PathBuf};

pub const TYPED: bool = true;

pub fn install(rt: &Rt, ns: &Ns) -> Result<()> {
    ns.def(rt, "print_payload", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["step"], &["check_print"])?;
        let step = PathBuf::from(b.req("step")?.str()?);
        let check_print = b.opt("check_print").unwrap_or(Val::Bool(false));
        print_payload(rt, &step, check_print)
    })?;
    Ok(())
}

pub fn main_block(_rt: &Rt) -> Result<()> {
    Ok(())
}

/// Keep the caller's print-check policy and return the Rust writer's readings.
///
/// `check_print` reaches the writer as the caller gave it (normally a bool).
pub fn print_payload(rt: &Rt, step: &Path, check_print: Val) -> Result<Val> {
    presentation::print_payload(rt, step, &presentation::Options { check_print, ..Default::default() })
}
