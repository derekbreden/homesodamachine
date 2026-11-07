//! The PET-GF cradle that holds the funnel's drain elbow, printed on the stock's bottom face: its
//! STEP, model file, payload and STL, and the numbers the installed machine hangs it by.
//!
//!     elbow-cradle [<output directory>]
mod cradle_geometry;
#[allow(dead_code)]
mod zone_files;
use anyhow::Result;
use hsm_kernel::part::write_part;
use hsm_kernel::{Body, v3};
use hsm_zone_c_numbers::cradle::cradle;
use serde_json::json;

fn main() -> Result<()> {
    let out = zone_files::out_dir("hardware/printed-parts/zone-c/funnel")?;
    let n = cradle();
    let printed = cradle_geometry::cradle(&n)?.translate(v3(0.0, 0.0, -n.block[3]));
    let said = write_part(&out, "elbow-cradle", &[Body { name: "elbow-cradle", color: Some(n.color), solid: &printed }])?;
    zone_files::json(&out.join("elbow-cradle.numbers.json"), &json!({"catch_gap": n.catch_gap, "block": n.block}))?;
    println!("{said}");
    Ok(())
}
