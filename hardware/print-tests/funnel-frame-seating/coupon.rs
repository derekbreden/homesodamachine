//! A front corner of the production funnel frame tests its flange, guide and screw ledge in the enclosure.
use anyhow::{Result, ensure};
use hsm_kernel::{Body, Solid, import, v3};
use hsm_kernel::part::write_part;
use hsm_sandbox::out;
use serde_json::json;

fn main() -> Result<()> {
    let output = out()?;
    let source = "hardware/printed-parts/zone-c/funnel/funnel-frame.step.npz";
    let mut models = import::model(source)?;
    ensure!(models.len() == 1, "one production frame");
    let model = models.remove(0);
    let top = model.solid.bounds().max.z;
    let low = v3(78.0, -84.0, 0.0);
    let high = v3(100.0, -31.0, top);
    let solid = model.solid.intersect(&Solid::cuboid(low, high))?;
    solid.check()?;
    ensure!(solid.components().len() == 1, "one connected seating coupon");
    let name = "funnel-frame-seating-coupon";
    write_part(&output, name, &[Body { name, color: model.color, solid: &solid }])?;
    let bounds = solid.bounds();
    let receipt = json!({
        "purpose": "Bind the seating coupon to the production front corner and its full print height.",
        "source": source,
        "crop_min_mm": low.to_array(),
        "crop_max_mm": high.to_array(),
        "actual_min_mm": bounds.min.to_array(),
        "actual_max_mm": bounds.max.to_array(),
        "production_base_z_mm": 0.0,
        "coupon_base_z_mm": bounds.min.z,
        "print_up_source": [0, 0, 1],
    });
    std::fs::write(output.join("geometry.json"), serde_json::to_vec_pretty(&receipt)?)?;
    println!("{receipt}");
    Ok(())
}
