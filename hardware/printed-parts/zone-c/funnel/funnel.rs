//! The cast silicone funnel: its STEP, model file and payload, and the numbers the installed
//! machine stands it by.
//!
//!     funnel [<output directory>]
#[allow(dead_code)]
mod funnel_geometry;
#[allow(dead_code)]
mod zone_files;
use anyhow::{Result, ensure};
use hsm_kernel::part::{AssemblyBody, write_assembly};
use hsm_zone_c_numbers::{catalog, funnel};
use serde_json::json;

fn main() -> Result<()> {
    let out = zone_files::out_dir("hardware/printed-parts/zone-c/funnel")?;
    let dims = funnel::dimensions();
    let (outside, cavity) = funnel_geometry::build_solids(&dims, 0.0, true, true)?;
    let funnel = outside.cut(&cavity)?;
    funnel.check()?;
    ensure!(funnel.components().len() == 1, "the funnel is one closed body");
    let size = funnel.bounds().size();
    let presentation = funnel.simplified_to((size.x + size.y + size.z) / 3.0 * catalog::VIEWER_DEFLECTION_RATIO)?;
    let body = AssemblyBody { name: "funnel", color: Some(catalog::silicone_black()), fine: &funnel, presentation: &presentation };
    let said = write_assembly(&out, "funnel", &[body], Some(&json!({})))?;
    zone_files::json(&out.join("funnel.numbers.json"), &json!({
        "top_z": dims.top_z,
        "end_z": dims.end_z,
        "ramp_z": [dims.ramp_z.0, dims.ramp_z.1],
        "bore_radius": dims.bore_radius,
        "drain_xy": [dims.drain_xy.0, dims.drain_xy.1],
    }))?;
    println!("{said}");
    Ok(())
}
