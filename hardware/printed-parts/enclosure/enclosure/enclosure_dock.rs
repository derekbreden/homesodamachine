//! The enclosure's four-channel factory tube-setting jig.
#[path = "enclosure_plan.rs"]
#[allow(dead_code)]
mod plan;

use anyhow::Result;
use hsm_kernel::part::{args, write_part};
use hsm_kernel::Body;

fn main() -> Result<()> {
    let (numbers, output) = args()?;
    let solid = plan::build(&numbers)?;
    let name = "enclosure-pump-tube-setting-jig";
    let bodies = [Body { name, color: Some(numbers.color("color")?), solid: &solid }];
    println!("{}", write_part(&output, name, &bodies)?);
    Ok(())
}
