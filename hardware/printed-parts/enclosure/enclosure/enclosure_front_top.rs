//! The front-top structural and printed part from private live Python records.
#[path = "enclosure_front_corner.rs"]
mod corner;
#[path = "enclosure_plan.rs"]
mod plan;
#[path = "enclosure_skin.rs"]
#[allow(dead_code)]
mod skin;
use anyhow::{Context, Result};
use hsm_kernel::part::{args, write_shown, Numbers};
use hsm_kernel::*;

pub(crate) fn build(n: &Numbers) -> Result<Solid> {
    corner::replace(plan::build(n)?.simplified()?, n)
}

fn main() -> Result<()> {
    let (n, out) = args()?;
    let solid = build(&n)?;
    // The complete structural model carries the CAD file's existing sliver cleanup.
    let model = solid.simplified()?;
    let mut said = write_shown(
        &out,
        "enclosure-front-top",
        &[Body {
            name: "enclosure-front-top",
            color: Some(n.color("color")?),
            solid: &model,
        }],
    )?;
    if n.get("field").is_ok() {
        let print_model = solid.simplified()?;
        let mut sources = flute_sources::Sources::new(&print_model);
        let shape = skin::flute_solid_observed(&print_model, &n, &[], &mut sources)?;
        plan::write_print_stl(&out.join("enclosure-front-top.stl"), &shape)?;
        let source_file = "enclosure-front-top.stl.sources.json";
        std::fs::write(out.join(source_file), serde_json::to_vec(&sources.document())?)?;
        said["files"]
            .as_array_mut()
            .context("part files")?
            .push(serde_json::json!("enclosure-front-top.stl"));
        said["files"].as_array_mut().unwrap().push(source_file.into());
        said["print"] = serde_json::json!({"volume":shape.volume(),"triangles":shape.num_tri()});
    }
    println!("{said}");
    Ok(())
}

#[path = "enclosure_flute_sources.rs"]
mod flute_sources;
