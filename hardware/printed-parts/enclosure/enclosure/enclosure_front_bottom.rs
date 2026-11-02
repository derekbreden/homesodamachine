//! Front-bottom fine geometry and its independent exterior print field.
#[path = "enclosure_plan.rs"]
#[allow(dead_code)]
mod plan;
#[path = "enclosure_skin.rs"]
#[allow(dead_code)]
mod skin;
use anyhow::{Context, Result};
use hsm_kernel::Body;
use hsm_kernel::part::{args, write_shown};

fn main() -> Result<()> {
    let (n, out) = args()?;
    let solid = plan::build(&n)?;
    let name = "enclosure-front-bottom";
    let mut said = write_shown(
        &out,
        name,
        &[Body {
            name,
            color: Some(n.color("color")?),
            solid: &solid,
        }],
    )?;
    if n.get("field").is_ok() {
        let printed = skin::flute_solid(&solid.simplified()?, &n, &[])?;
        plan::write_print_stl(&out.join("enclosure-front-bottom.stl"), &printed)?;
        said["files"]
            .as_array_mut()
            .context("part files")?
            .push(serde_json::json!("enclosure-front-bottom.stl"));
        said["print"] =
            serde_json::json!({"volume":printed.volume(),"triangles":printed.num_tri()});
    }
    println!("{said}");
    Ok(())
}
