//! Native process control supplies host admission, CAD coordination and immutable runtime installation.
use super::*;
use std::{collections::BTreeMap, os::fd::IntoRawFd};

pub mod cad;
pub mod install;
pub mod runner;
pub mod slots;

pub(crate) fn text(value: &Value) -> Result<&str> {
    value.as_str().context("runtime string")
}
