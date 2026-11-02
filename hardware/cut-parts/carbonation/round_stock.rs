//! The fine model and analytic quote STEP share the stock's Python numbers.
use anyhow::{Context, Result};
use hsm_kernel::part::{args, write_shown_with_step};
use hsm_kernel::step::{AxialBore, RoundStock};
use hsm_kernel::{Body, v2};

pub fn main() -> Result<()> {
    let (n, out) = args()?;
    let bores = n.get("bores")?.as_array().context("bores must be an array")?
        .iter().map(|b| -> Result<AxialBore> {
            let center = b["center"].as_array().context("bore needs a centre")?;
            anyhow::ensure!(center.len() == 2, "bore centre needs two coordinates");
            Ok(AxialBore {
                center: v2(center[0].as_f64().context("bore X")?, center[1].as_f64().context("bore Y")?),
                radius: b["radius"].as_f64().context("bore radius")?,
                floor: b["floor"].as_f64().context("bore floor")?,
            })
        }).collect::<Result<Vec<_>>>()?;
    let stock = RoundStock { radius: n.f("radius")?, height: n.f("height")?, bores };
    let solid = stock.solid()?;
    let color = Some(n.color("color")?);
    let name = n.text("name")?;
    let quote = stock.step_bytes(name, color)?;
    let bodies = [Body { name, color, solid: &solid }];
    println!("{}", write_shown_with_step(&out, name, &bodies, quote)?);
    Ok(())
}
