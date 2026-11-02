//! The current lower pump retainer, with relaxed print or installed wing controls.
#[path = "enclosure_plan.rs"]
#[allow(dead_code)]
mod plan;
use anyhow::Result;
use hsm_kernel::Body;
use hsm_kernel::part::{args, write_part, write_shown};

fn main() -> Result<()> {
    let (n, out) = args()?;
    let solid = plan::build(&n)?;
    let name = n.text("name")?;
    let bodies = [Body {
        name,
        color: Some(n.color("color")?),
        solid: &solid,
    }];
    let said = if n.get("seated")?.as_bool() == Some(true) {
        write_shown(&out, name, &bodies)?
    } else {
        write_part(&out, name, &bodies)?
    };
    println!("{said}");
    Ok(())
}
