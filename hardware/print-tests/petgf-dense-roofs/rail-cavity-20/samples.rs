// samples.rs crops the complete rail section and retains its production floor, arm and catch stock.
use anyhow::{Context, Result, ensure};
use hsm_kernel::{Font, HAlign, Kind, Plane, Solid, VAlign, stl_bytes, v3};
use serde_json::{Value, json};

fn point(v: &Value) -> Result<hsm_kernel::V3> {
    Ok(v3(v[0].as_f64().context("x")?, v[1].as_f64().context("y")?, v[2].as_f64().context("z")?))
}

fn main() -> Result<()> {
    let dir = hsm_sandbox::out()?;
    let mut spec: Value = serde_json::from_slice(&std::fs::read(dir.join("inputs/spec.json"))?)?;
    let font = Font::find("Helvetica Neue", Kind::Bold)?;
    let label_height = spec["label_height_mm"].as_f64().context("label height")?;
    let mut output = Vec::new();
    for family in spec["families"].as_array_mut().context("families")? {
        let id = family["id"].as_str().context("family id")?.to_owned();
        let input = dir.join("inputs").join(format!("{id}.npz"));
        let source = hsm_kernel::import::model(input)?;
        let crop = source[0].solid.intersect(&Solid::cuboid(point(&family["crop_min_mm"])? ,point(&family["crop_max_mm"])?))?;
        ensure!(crop.components().len() == 1, "{id} needs a connected production crop");
        let min_z = crop.bounds().min.z;
        let label_center = point(&family["label_center_world_mm"])?;
        family["actual_crop_min_z_mm"] = json!(min_z);
        for condition in ["D"] {
            let name = format!("{id}{condition}");
            let letters = Plane::XY.text(&font, &name, 3., label_height + 0.05,
                HAlign::Center, VAlign::Center)?.translate(label_center - v3(0., 0., 0.05));
            let labeled = crop.union(&letters)?;
            ensure!(labeled.components().len() == 1, "{name} label attaches to existing top stock");
            let printed = labeled.translate(v3(0., 0., -min_z));
            printed.check()?;
            std::fs::write(dir.join(format!("{name}.stl")), stl_bytes(&[&printed])?)?;
            let b = printed.bounds();
            output.push(json!({"id":name,"family":id,"condition":condition,
                "bounds_mm":[[b.min.x,b.min.y,b.min.z],[b.max.x,b.max.y,b.max.z]],
                "volume_mm3":printed.volume(),"world_z_to_print_z_mm":-min_z,
                "watertight":true,"solids":1}));
        }
    }
    std::fs::write(dir.join("geometry.json"), serde_json::to_vec_pretty(&json!({"spec":spec,"specimens":output}))?)?;
    println!("{}", dir.join("geometry.json").display());
    Ok(())
}
