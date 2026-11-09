//! Cut the CO2 fit variants from the approved tile, retaining its bore, lettering and thickness.
use anyhow::{Result, Context};
use hsm_kernel::{Body, Solid, v3};
use serde_json::{Value, json};
use std::path::Path;
fn main() -> Result<()> {
    let args: Vec<String> = std::env::args().collect();
    let spec: Value = serde_json::from_slice(&std::fs::read(&args[1])?)?;
    let out = Path::new(&args[2]); std::fs::create_dir_all(out)?;
    let source = spec["source"].as_str().context("source path")?;
    let model = hsm_kernel::import::model(source)?;
    let base = hsm_kernel::import::body(&model, "bulkhead-ring-co2")?;
    let ink = hsm_kernel::import::body(&model, "bulkhead-ring-co2-word")?;
    let bounds = base.bounds();
    let mut records = Vec::new();
    for variant in spec["variants"].as_array().context("variants")? {
        let id = variant["id"].as_str().context("variant id")?;
        let trim = variant["per_side_reduction_mm"].as_f64().context("edge trim")?;
        let clip = Solid::cuboid(v3(bounds.min.x + trim, bounds.min.y - 1., bounds.min.z - 1.),
                                  v3(bounds.max.x - trim, bounds.max.y + 1., bounds.max.z + 1.));
        let tile = base.intersect(&clip)?;
        let name = format!("co2-fit-{}", id.to_lowercase());
        let bodies = [Body {name:"bulkhead-ring-co2", color:model[0].color, solid:&tile},
                      Body {name:"bulkhead-ring-co2-word", color:model[1].color, solid:ink}];
        let files = hsm_kernel::part::write_part(out, &name, &bodies)?;
        records.push(json!({"id":id,"per_side_reduction_mm":trim,"width_mm":tile.bounds().max.x-tile.bounds().min.x,"files":files}));
    }
    std::fs::write(out.join("geometry.json"), serde_json::to_string_pretty(&json!({"variants":records}))? + "\n")?;
    println!("{}", out.join("geometry.json").display());
    Ok(())
}
